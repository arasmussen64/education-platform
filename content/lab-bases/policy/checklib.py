"""The policy labs' check library (content/lab-bases/policy/README.md).

A check on a learner's Cedar policies must not be passable by a policy that
names this lab's people, so a check makes up its requests when it runs:

    import sys
    sys.path.insert(0, "/usr/local/lib/policy")
    from checklib import Names, Case, combine, sides, entity, ref, uid, check

    names = Names()
    cases = []
    for c in combine(same_store=[True, False], amount=sides(100)):
        store, other = names.new("store"), names.new("store")
        clerk, order = names.new("staff"), names.new("order")
        cases.append(Case(
            words=f"support staff, {'own' if c['same_store'] else 'another'} "
                  f"store, viewing an order of {c['amount']}",
            principal=uid("Staff", clerk), action=uid("Action", "view"),
            resource=uid("Order", order), context={"mfa": True},
            entities=[entity("Role", "support"),
                      entity("Staff", clerk, {"store": store}, [("Role", "support")]),
                      entity("Order", order, {"store": store if c["same_store"] else other,
                                              "amount": c["amount"]})],
            allow=c["same_store"]))
    check("/home/learner/shop/policies.cedar", cases, schema="/home/learner/shop/shop.cedarschema")

check() prints "ok", or the first three cases where the learner's policy and
the rules disagree, in the case's own words, and ends with status 0 either
way (a lab's check compares what it prints with "ok").

Standard library only: it runs on the lab image's Python 3.12 and in the
repository's tests (tools/tests/test_policy_checklib.py).
"""

import itertools
import json
import os
import re
import secrets
import subprocess
import tempfile

CEDAR = "cedar"  # the tests point this at a stand-in


class PolicyError(Exception):
    """Cedar couldn't use the policies (or the check's own cases) at all."""


# --- names nobody could have written in advance ------------------------------


class Names:
    """Makes names that are new in every run and never repeat within one:
    names.new("staff") gives "staff-3f9a2c", then "staff-b01d77", ...
    The random part is hex, so a name never starts with "-" and never needs
    quoting in a shell."""

    def __init__(self, token=secrets.token_hex):
        self._token = token
        self._used = set()

    def new(self, kind):
        while True:
            name = f"{kind}-{self._token(3)}"
            if name not in self._used:
                self._used.add(name)
                return name


# --- the cases of a rule -----------------------------------------------------


def combine(**dimensions):
    """Every combination of the named dimensions' values, each as a dict:
    combine(role=["support", "finance"], mfa=[True, False]) gives four."""
    keys = list(dimensions)
    return [
        dict(zip(keys, values, strict=True))
        for values in itertools.product(*(dimensions[key] for key in keys))
    ]


def sides(limit, randbelow=secrets.randbelow):
    """The numbers that try a rule "up to LIMIT": the limit itself and the
    number just past it, always both, with one well below and one well above
    that change from run to run. A policy that says "< 100" for "<= 100", or
    "== 100", then fails every run instead of some."""
    below = max(0, limit - 2 - randbelow(max(1, limit // 2)))
    above = limit + 2 + randbelow(max(1, limit))
    return [below, limit, limit + 1, above]


class Case:
    """One made-up request: who asks to do what to what, the entities that
    exist while they ask, what the rules say (allow: True or False), and
    how to say the case to a learner (words)."""

    def __init__(
        self, words, principal, action, resource, entities, allow, context=None
    ):
        self.words = words
        self.principal = principal
        self.action = action
        self.resource = resource
        self.entities = entities
        self.allow = bool(allow)
        self.context = context or {}


def uid(kind, name):
    """A Cedar entity's name as a request writes it: Staff::"alice"."""
    return f'{kind}::"{name}"'


def ref(kind, name):
    """A Cedar entity as an attribute's value (an order's handled_by)."""
    return {"__entity": {"type": kind, "id": name}}


def entity(kind, name, attrs=None, parents=()):
    """One entity for a case's entities list; parents are (kind, name) pairs."""
    return {
        "uid": {"type": kind, "id": name},
        "attrs": attrs or {},
        "parents": [{"type": k, "id": n} for k, n in parents],
    }


# --- asking Cedar ------------------------------------------------------------

RESULT = re.compile(r"^\s*test case-(\d+) \.\.\. (ok|fail|error)\b(.*)$")


def decide(policies, cases, schema=None, run=subprocess.run):
    """What the policies in the file say to each case: a list of True
    (allow) and False (deny), in the cases' order. All the cases go to one
    "cedar run-tests", a few hundred in well under a second. Only the
    decision is compared: which policy decided is the learner's business."""
    if not os.path.isfile(policies):
        raise PolicyError(f"there is no file {policies}")
    tests = [
        {
            "name": f"case-{number}",
            "request": {
                "principal": case.principal,
                "action": case.action,
                "resource": case.resource,
                "context": case.context,
            },
            "entities": case.entities,
            "decision": "allow" if case.allow else "deny",
            "reason": [],
            "num_errors": 0,
        }
        for number, case in enumerate(cases)
    ]
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "tests.json")
        with open(path, "w", encoding="utf-8") as file:
            json.dump(tests, file)
        command = [
            CEDAR,
            "run-tests",
            "-f",
            "plain",
            "--policies",
            policies,
            "--tests",
            path,
        ]
        if schema:
            command += ["--schema", schema]
        done = run(command, capture_output=True, text=True, check=False)
    said = {}
    lines = done.stdout.splitlines()
    for at, line in enumerate(lines):
        found = RESULT.match(line)
        if not found:
            continue
        number, verdict, rest = int(found.group(1)), found.group(2), found.group(3)
        expected = cases[number].allow
        if verdict == "ok":
            said[number] = expected
        elif verdict == "fail" and "expected" in rest:
            said[number] = not expected
        else:
            # What Cedar says about one test runs to the next blank line.
            said_here = []
            for following in lines[at + 1 :]:
                if not following.strip():
                    break
                said_here.append(following)
            detail = first_cause("\n".join(said_here))
            if "policy set validation failed" in detail:
                # With a schema, Cedar validates the policies before every
                # test: the learner's mistake, not the case's.
                cause = detail.replace("policy set validation failed; ", "")
                raise PolicyError(
                    f"the policies don't validate against the schema: {cause} "
                    "(cedar validate shows the line)"
                )
            raise PolicyError(
                f"the check's own case {number + 1} ({cases[number].words}) "
                f"can't be asked: {detail}"
            )
    if len(said) != len(cases):
        why = first_cause(done.stderr or done.stdout)
        raise PolicyError(f"Cedar can't read the policies: {why}")
    return [said[number] for number in range(len(cases))]


def first_cause(output):
    """The first useful lines of what Cedar printed with "-f plain"."""
    keep = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith(("Diagnostic severity", "Begin snippet")):
            continue
        keep.append(line.replace("Caused by: ", ""))
        if len(keep) == 4:
            break
    return "; ".join(keep) or "it printed nothing"


def disagreements(policies, cases, schema=None, run=subprocess.run):
    """The cases where the policies and the rules disagree, each as the
    sentence a learner reads."""
    found = []
    for case, allowed in zip(cases, decide(policies, cases, schema, run), strict=True):
        if allowed != case.allow:
            rules = "allow" if case.allow else "deny"
            yours = "allow" if allowed else "deny"
            found.append(
                f"{case.words}: the rules say {rules}, your policy says {yours}"
            )
    return found


def report(found, total, show=3):
    """What a check prints: "ok", or the first few disagreements."""
    if not found:
        return "ok"
    lines = found[:show]
    if len(found) > show:
        lines.append(f"(and {len(found) - show} more of the {total} cases tried)")
    return "\n".join(lines)


def check(policies, cases, schema=None, run=subprocess.run):
    """Prints "ok" or what disagrees, for a check that expects "ok"."""
    if not cases:
        raise ValueError("a check with no cases would pass anything")
    try:
        print(report(disagreements(policies, cases, schema, run), len(cases)))
    except PolicyError as error:
        print(error)


def validates(schema, policies, run=subprocess.run):
    """ "ok" when cedar validate accepts the policies against the schema,
    or Cedar's own first reason, which names the policy and the line."""
    for path in (schema, policies):
        if not os.path.isfile(path):
            return f"there is no file {path}"
    done = run(
        [CEDAR, "validate", "-f", "plain", "--schema", schema, "--policies", policies],
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode == 0:
        return "ok"
    return "the policies don't validate: " + first_cause(done.stderr or done.stdout)


# --- shared by ask and access-review -----------------------------------------


def load_entities(path):
    try:
        with open(path, encoding="utf-8") as file:
            entities = json.load(file)
    except OSError:
        raise PolicyError(f"there is no file {path}") from None
    except ValueError as error:
        raise PolicyError(f"{path} isn't valid JSON: {error}") from None
    if not isinstance(entities, list):
        raise PolicyError(f"{path} should be a JSON list of entities")
    return entities


def find_entity(name, entities, what, kinds=None):
    """Staff::"alice" for "alice": the one entity with that name (of the
    kinds given, if any). A full Type::"name" is taken as written."""
    if "::" in name:
        return name
    found = sorted(
        {
            e["uid"]["type"]
            for e in entities
            if e.get("uid", {}).get("id") == name
            and (kinds is None or e["uid"]["type"] in kinds)
        }
    )
    if len(found) == 1:
        return uid(found[0], name)
    if not found:
        raise PolicyError(f'there is no {what} called "{name}" in the entities file')
    choices = " or ".join(uid(kind, name) for kind in found)
    raise PolicyError(f'"{name}" could be {choices}: write the one you mean in full')


def authorize(
    policies,
    entities_path,
    principal,
    action,
    resource,
    context,
    schema=None,
    run=subprocess.run,
):
    """One request through "cedar authorize -v": (allowed, [deciding policy
    ids], [errors Cedar reported])."""
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "request.json")
        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "principal": principal,
                    "action": action,
                    "resource": resource,
                    "context": context,
                },
                file,
            )
        command = [CEDAR, "authorize", "-v", "-f", "plain", "--policies", policies]
        command += ["--entities", entities_path, "--request-json", path]
        if schema:
            command += ["--schema", schema]
        done = run(command, capture_output=True, text=True, check=False)
    lines = [line.strip() for line in (done.stdout + "\n" + done.stderr).splitlines()]
    if "ALLOW" not in lines and "DENY" not in lines:
        raise PolicyError(first_cause(done.stderr or done.stdout))
    deciding, errors, listing = [], [], False
    for line in lines:
        if line.startswith("note: this decision was due to"):
            listing = True
        elif line.startswith("error while evaluating"):
            errors.append(line)
        elif listing and line and not line.startswith("note:"):
            deciding.append(line)
        elif not line:
            listing = False
    return "ALLOW" in lines, deciding, errors
