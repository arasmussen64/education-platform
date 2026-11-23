"""The policy lab base's check library and its two Cedar helpers
(content/lab-bases/policy/: checklib.py, bin/ask, bin/access-review).

The policy labs' checks decide right from wrong with checklib: it makes up
the requests, hands them to the Cedar command-line tool and reads the
verdicts. Cedar itself isn't on the machine these tests run on (it is in
the lab image, where the probe lab's contract runs it for real), so here a
stand-in answers in Cedar's own words, copied from the pinned tool's output
on 2026-11-22. What is tested is everything around it: that both sides of
every number in a rule are always tried, that no name repeats, that only
the decision is compared, and that a learner is told what disagrees in
words.
"""

import datetime
import importlib.machinery
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "content" / "lab-bases" / "policy"


def load(name: str, path: Path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


checklib = load("checklib", BASE / "checklib.py")
ask = load("policy_ask", BASE / "bin" / "ask")
access_review = load("policy_access_review", BASE / "bin" / "access-review")


# --- the generator --------------------------------------------------------------


def test_combine_gives_every_combination_once() -> None:
    cases = checklib.combine(role=["support", "finance"], mfa=[True, False], n=[1])
    assert len(cases) == 4
    assert {"role": "finance", "mfa": True, "n": 1} in cases
    assert len({json.dumps(case, sort_keys=True) for case in cases}) == 4
    assert checklib.combine() == [{}]


def test_sides_always_has_both_sides_of_the_limit() -> None:
    # One case drawn at random from 100 and 101 let "< 100" pass whenever
    # 101 came up (the designer's finding): both are always there.
    for limit in [1, 2, 100, 5000]:
        for _ in range(200):
            below, at, past, above = checklib.sides(limit)
            assert (at, past) == (limit, limit + 1)
            assert 0 <= below < limit and above > limit + 1
    assert len({tuple(checklib.sides(100)) for _ in range(50)}) > 1


def test_names_never_repeat_and_never_need_quoting() -> None:
    names = checklib.Names()
    made = [names.new("staff") for _ in range(500)]
    assert len(set(made)) == 500
    for name in made:
        kind, _, tail = name.partition("-")
        assert kind == "staff" and len(tail) == 6
        assert set(tail) <= set("0123456789abcdef")
    # Even a source that repeats itself is asked again until the name is new.
    tokens = iter(["aaaaaa", "aaaaaa", "aaaaaa", "bbbbbb"])
    names = checklib.Names(token=lambda _: next(tokens))
    assert [names.new("store"), names.new("store")] == ["store-aaaaaa", "store-bbbbbb"]
    assert checklib.Names().new("order") != checklib.Names().new("order")


def test_the_entity_helpers_write_cedars_json() -> None:
    assert checklib.uid("Staff", "alice") == 'Staff::"alice"'
    assert checklib.ref("Staff", "wen") == {"__entity": {"type": "Staff", "id": "wen"}}
    assert checklib.entity("Staff", "alice", {"store": "n"}, [("Role", "support")]) == {
        "uid": {"type": "Staff", "id": "alice"},
        "attrs": {"store": "n"},
        "parents": [{"type": "Role", "id": "support"}],
    }


# --- a stand-in for the Cedar tool -----------------------------------------------


class FakeCedar:
    """Answers "cedar run-tests" as the pinned tool does, deciding each
    request with a Python function in place of a policy file."""

    def __init__(self, policy=None, parse_error=None, invalid=None, bad_case=None):
        self.policy, self.parse_error = policy, parse_error
        self.invalid, self.bad_case = invalid, bad_case
        self.commands: list[list[str]] = []
        self.tests: list[dict] = []

    def __call__(self, command, **_kwargs):
        self.commands.append(command)
        if self.parse_error:
            return subprocess.CompletedProcess(command, 1, "", self.parse_error)
        self.tests = json.loads(
            Path(command[command.index("--tests") + 1]).read_text(encoding="utf-8")
        )
        lines, failed = [f"running {len(self.tests)} test(s)"], 0
        for number, test in enumerate(self.tests):
            if self.invalid:
                lines += [f"  test {test['name']} ... error:", *self.invalid, ""]
                failed += 1
            elif number == self.bad_case:
                lines += [
                    f"  test {test['name']} ... error:",
                    "failed to parse entities: entity does not conform to the schema",
                    "",
                ]
                failed += 1
            else:
                allowed = self.policy(test)
                expected = test["decision"] == "allow"
                if allowed == expected:
                    lines.append(f"  test {test['name']} ... ok")
                else:
                    said = ("Allow", "Deny") if expected else ("Deny", "Allow")
                    lines.append(
                        f"  test {test['name']} ... fail: "
                        f"expected {said[0]}, got {said[1]}"
                    )
                    failed += 1
        lines.append(f"results: {len(self.tests) - failed} passed, {failed} failed")
        return subprocess.CompletedProcess(
            command, 1 if failed else 0, "\n".join(lines), ""
        )


# The shop's rules, as the probe lab and the topic's worked example have
# them: support staff view and refund in their own store, refunds up to 100,
# never an order they handled, never without MFA.
LIMIT = 100


def shop_cases(names):
    cases = []
    for c in checklib.combine(
        role=["support", "warehouse", None],
        action=["view", "refund", "export"],
        same_store=[True, False],
        amount=checklib.sides(LIMIT),
        own=[True, False],
        mfa=[True, False],
    ):
        store, elsewhere = names.new("store"), names.new("store")
        person, colleague = names.new("staff"), names.new("staff")
        order = names.new("order")
        allow = c["role"] == "support" and c["same_store"]
        if c["action"] == "refund":
            allow = allow and c["amount"] <= LIMIT and not c["own"] and c["mfa"]
        elif c["action"] == "export":
            allow = False
        cases.append(
            checklib.Case(
                words=(
                    f"{c['role'] or 'no role'}, {c['action']}, "
                    f"{'own' if c['same_store'] else 'another'} store, {c['amount']}, "
                    f"{'own order' if c['own'] else "a colleague's order"}, "
                    f"{'MFA' if c['mfa'] else 'no MFA'}"
                ),
                principal=checklib.uid("Staff", person),
                action=checklib.uid("Action", c["action"]),
                resource=checklib.uid("Order", order),
                context={"mfa": c["mfa"]},
                entities=[
                    checklib.entity("Role", "support"),
                    checklib.entity(
                        "Staff",
                        person,
                        {"store": store},
                        [("Role", c["role"])] if c["role"] else [],
                    ),
                    checklib.entity("Staff", colleague, {"store": store}),
                    checklib.entity(
                        "Order",
                        order,
                        {
                            "store": store if c["same_store"] else elsewhere,
                            "amount": c["amount"],
                            "handled_by": checklib.ref(
                                "Staff", person if c["own"] else colleague
                            ),
                        },
                    ),
                ],
                allow=allow,
            )
        )
    return cases


def facts(test):
    """What a policy can see in one generated test, as plain values."""
    entities = {(e["uid"]["type"], e["uid"]["id"]): e for e in test["entities"]}
    kind, _, name = test["request"]["principal"].partition("::")
    person = entities[(kind, name.strip('"'))]
    kind, _, name = test["request"]["resource"].partition("::")
    order = entities[(kind, name.strip('"'))]
    return {
        "support": {"type": "Role", "id": "support"} in person["parents"],
        "action": test["request"]["action"].split("::")[1].strip('"'),
        "store": person["attrs"]["store"],
        "order_store": order["attrs"]["store"],
        "amount": order["attrs"]["amount"],
        "own": order["attrs"]["handled_by"]["__entity"]["id"] == person["uid"]["id"],
        "mfa": test["request"]["context"]["mfa"],
        "person": person["uid"]["id"],
    }


def reference(
    test,
    limit=lambda amount: amount <= LIMIT,
    forbid_own=True,
    need_mfa=True,
    any_role=False,
    any_store=False,
    export=False,
):
    f = facts(test)
    if f["action"] == "export" and not export:
        return False
    permitted = (f["support"] or any_role) and (
        f["store"] == f["order_store"] or any_store
    )
    if f["action"] != "refund":
        return permitted
    if forbid_own and f["own"]:
        return False
    if need_mfa and not f["mfa"]:
        return False
    return permitted and limit(f["amount"])


# name: a policy that is wrong in one way, as a learner's would be.
WRONG_POLICIES = {
    "allow-all": lambda t: reference(t, any_role=True, any_store=True, export=True),
    "no-self-refund-forbid": lambda t: reference(t, forbid_own=False),
    "mfa-not-asked": lambda t: reference(t, need_mfa=False),
    "under-the-limit": lambda t: reference(t, limit=lambda amount: amount < LIMIT),
    "exactly-the-limit": lambda t: reference(t, limit=lambda amount: amount == LIMIT),
    "no-limit": lambda t: reference(t, limit=lambda amount: True),
    "any-store": lambda t: reference(t, any_store=True),
    "store-named": lambda t: reference(t) and facts(t)["store"] == "north",
    "person-named": lambda t: reference(t) and facts(t)["person"] == "alice",
    "deny-all": lambda t: False,
}


@pytest.fixture
def policies(tmp_path) -> str:
    path = tmp_path / "policies.cedar"
    path.write_text("// the stand-in decides\n", encoding="utf-8")
    return str(path)


def test_the_reference_policy_agrees_on_every_case(policies) -> None:
    cases = shop_cases(checklib.Names())
    assert len(cases) == 3 * 3 * 2 * 4 * 2 * 2
    assert checklib.disagreements(policies, cases, run=FakeCedar(reference)) == []
    assert sum(case.allow for case in cases) > 10  # allowing matters as much as denying


@pytest.mark.parametrize("name", sorted(WRONG_POLICIES))
def test_a_wrong_policy_disagrees_in_every_run(policies, name) -> None:
    # Random names and random far amounts: a wrong policy must be caught
    # whatever they come out as, not in most runs.
    for _ in range(6):
        cases = shop_cases(checklib.Names())
        found = checklib.disagreements(
            policies, cases, run=FakeCedar(WRONG_POLICIES[name])
        )
        assert found, name


# --- the driver ---------------------------------------------------------------


def test_only_the_decision_is_compared(policies) -> None:
    fake = FakeCedar(reference)
    cases = shop_cases(checklib.Names())[:5]
    decisions = checklib.decide(policies, cases, schema="shop.cedarschema", run=fake)
    assert decisions == [case.allow for case in cases]
    # Each test names no deciding policy and expects no error, which is
    # what makes run-tests compare the decision alone (it refuses a test
    # without the two fields).
    assert all(t["reason"] == [] and t["num_errors"] == 0 for t in fake.tests)
    assert [t["name"] for t in fake.tests] == [f"case-{n}" for n in range(5)]
    assert fake.tests[0]["request"]["principal"] == cases[0].principal
    command = fake.commands[0]
    assert command[:2] == ["cedar", "run-tests"]
    assert command[command.index("--policies") + 1] == policies
    assert command[command.index("--schema") + 1] == "shop.cedarschema"
    fake = FakeCedar(reference)
    checklib.decide(policies, cases, run=fake)
    assert "--schema" not in fake.commands[0]


def test_a_disagreement_is_said_in_the_cases_own_words(policies, capsys) -> None:
    cases = shop_cases(checklib.Names())
    fake = FakeCedar(WRONG_POLICIES["deny-all"])
    found = checklib.disagreements(policies, cases, run=fake)
    allowed = [case for case in cases if case.allow]
    assert found == [
        f"{case.words}: the rules say allow, your policy says deny" for case in allowed
    ]
    checklib.check(policies, cases, run=fake)
    printed = capsys.readouterr().out.splitlines()
    assert printed[:3] == found[:3]
    assert printed[3] == f"(and {len(found) - 3} more of the {len(cases)} cases tried)"
    assert len(printed) == 4
    checklib.check(policies, cases, run=FakeCedar(reference))
    assert capsys.readouterr().out == "ok\n"


def test_the_report_shows_at_most_three() -> None:
    assert checklib.report([], 10) == "ok"
    assert checklib.report(["a", "b", "c"], 10) == "a\nb\nc"
    said = checklib.report(["a", "b", "c", "d"], 10)
    assert said == "a\nb\nc\n(and 1 more of the 10 cases tried)"


def test_policies_cedar_cant_parse_are_said_once_in_its_words(policies, capsys) -> None:
    # "cedar run-tests -f plain" on a file with an unclosed bracket.
    error = (
        "failed to parse policy set\n"
        "    Diagnostic severity: error\n"
        "    Caused by: unexpected end of input\n"
        "Begin snippet starting at line 1, column 1\n"
        "\n"
        "snippet line 1: permit (principal, action, resource\n"
        "    label at line 1, column 36: expected `!=`, `)`, `,`\n"
    )
    cases = shop_cases(checklib.Names())[:3]
    with pytest.raises(checklib.PolicyError) as raised:
        checklib.decide(policies, cases, run=FakeCedar(parse_error=error))
    assert str(raised.value) == (
        "Cedar can't read the policies: failed to parse policy set; "
        "unexpected end of input; snippet line 1: permit (principal, action, "
        "resource; label at line 1, column 36: expected `!=`, `)`, `,`"
    )
    checklib.check(policies, cases, run=FakeCedar(parse_error=error))
    assert capsys.readouterr().out.startswith("Cedar can't read the policies: ")


def test_policies_the_schema_refuses_are_the_learners_not_the_cases(policies) -> None:
    # With a schema, run-tests validates the policies before each test and
    # every test "errors": that must not read as a broken check.
    invalid = [
        "policy set validation failed",
        "    Diagnostic severity: error",
        "    Caused by: for policy `policy0`, attribute `stor` on entity type "
        "`Staff` not found",
    ]
    cases = shop_cases(checklib.Names())[:3]
    with pytest.raises(checklib.PolicyError) as raised:
        checklib.decide(policies, cases, run=FakeCedar(invalid=invalid))
    assert str(raised.value) == (
        "the policies don't validate against the schema: for policy `policy0`, "
        "attribute `stor` on entity type `Staff` not found "
        "(cedar validate shows the line)"
    )


def test_a_case_cedar_refuses_is_reported_as_the_checks_own_fault(policies) -> None:
    cases = shop_cases(checklib.Names())[:3]
    with pytest.raises(checklib.PolicyError) as raised:
        checklib.decide(policies, cases, run=FakeCedar(reference, bad_case=1))
    assert str(raised.value) == (
        f"the check's own case 2 ({cases[1].words}) can't be asked: "
        "failed to parse entities: entity does not conform to the schema"
    )


def test_a_missing_policy_file_and_a_check_with_no_cases(tmp_path, policies) -> None:
    missing = str(tmp_path / "nowhere.cedar")
    with pytest.raises(checklib.PolicyError, match="there is no file"):
        checklib.decide(missing, shop_cases(checklib.Names())[:1])
    with pytest.raises(ValueError, match="would pass anything"):
        checklib.check(policies, [])


def test_validates_gives_ok_or_cedars_first_reason(tmp_path, policies) -> None:
    schema = tmp_path / "shop.cedarschema"
    schema.write_text("entity Role;\n", encoding="utf-8")

    def accepts(command, **_):
        assert command[1:4] == ["validate", "-f", "plain"]
        return subprocess.CompletedProcess(
            command, 0, "policy set validation passed", ""
        )

    def refuses(command, **_):
        error = (
            "policy set validation failed\n    Diagnostic severity: error\n"
            "    Caused by: for policy `policy0`, attribute `stor` on entity type "
            "`Staff` not found\nBegin snippet starting at line 1, column 1\n"
        )
        return subprocess.CompletedProcess(command, 3, "", error)

    assert checklib.validates(str(schema), policies, run=accepts) == "ok"
    assert checklib.validates(str(schema), policies, run=refuses) == (
        "the policies don't validate: policy set validation failed; for policy "
        "`policy0`, attribute `stor` on entity type `Staff` not found"
    )
    said = checklib.validates(str(tmp_path / "none.cedarschema"), policies)
    assert said.startswith("there is no file")


# --- what ask and access-review share -------------------------------------------

ENTITIES = [
    checklib.entity("Staff", "alice"),
    checklib.entity("Order", "o-1"),
    checklib.entity("Staff", "sam"),
    checklib.entity("Service", "sam"),
]


def test_a_bare_name_finds_its_one_entity() -> None:
    assert checklib.find_entity("alice", ENTITIES, "principal") == 'Staff::"alice"'
    assert checklib.find_entity('Order::"x"', ENTITIES, "resource") == 'Order::"x"'
    with pytest.raises(checklib.PolicyError) as raised:
        checklib.find_entity("bob", ENTITIES, "principal")
    assert (
        str(raised.value) == 'there is no principal called "bob" in the entities file'
    )
    with pytest.raises(checklib.PolicyError) as raised:
        checklib.find_entity("sam", ENTITIES, "principal")
    assert str(raised.value) == (
        '"sam" could be Service::"sam" or Staff::"sam": write the one you mean in full'
    )
    assert checklib.find_entity("sam", ENTITIES, "x", kinds=["Staff"]) == 'Staff::"sam"'


def test_entities_that_arent_a_json_list_are_refused(tmp_path) -> None:
    path = tmp_path / "entities.json"
    with pytest.raises(checklib.PolicyError, match="there is no file"):
        checklib.load_entities(str(path))
    path.write_text("[{", encoding="utf-8")
    with pytest.raises(checklib.PolicyError, match="isn't valid JSON"):
        checklib.load_entities(str(path))
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(checklib.PolicyError, match="should be a JSON list"):
        checklib.load_entities(str(path))


# "cedar authorize -v" as the pinned tool printed it on 2026-11-22.
ALLOWED = (
    "\nALLOW\n\nnote: this decision was due to the following policies:\n  policy1\n\n"
)
TWO_FORBIDS = (
    "\nDENY\n\nnote: this decision was due to the following policies:\n"
    "  no-self-refund\n  policy3\n\n"
)
NOTHING_APPLIES = "\nDENY\n\nnote: no policies applied to this request\n"
SKIPPED = (
    '\nDENY\n\nerror while evaluating policy `support-view`: `Staff::"alice"` '
    "does not have the attribute `stor`\n\nnote: no policies applied to this request\n"
)


@pytest.mark.parametrize(
    "printed, status, expected",
    [
        (ALLOWED, 0, (True, ["policy1"], [])),
        (TWO_FORBIDS, 2, (False, ["no-self-refund", "policy3"], [])),
        (NOTHING_APPLIES, 2, (False, [], [])),
        (
            SKIPPED,
            2,
            (
                False,
                [],
                [
                    "error while evaluating policy `support-view`: "
                    '`Staff::"alice"` does not have the attribute `stor`'
                ],
            ),
        ),
    ],
)
def test_authorize_reads_the_decision_and_who_decided(
    printed, status, expected
) -> None:
    asked = {}

    def cedar(command, **_):
        request = Path(command[command.index("--request-json") + 1])
        asked.update(json.loads(request.read_text(encoding="utf-8")))
        return subprocess.CompletedProcess(command, status, printed, "")

    got = checklib.authorize(
        "p.cedar", "e.json", 'Staff::"alice"', 'Action::"view"', 'Order::"o-1"',
        {"mfa": True}, run=cedar,
    )  # fmt: skip
    assert got == expected
    assert asked == {
        "principal": 'Staff::"alice"',
        "action": 'Action::"view"',
        "resource": 'Order::"o-1"',
        "context": {"mfa": True},
    }


def test_authorize_raises_what_cedar_said_when_it_gave_no_decision() -> None:
    def cedar(command, **_):
        error = "failed to parse request\n    Caused by: context `{}` is not valid\n"
        return subprocess.CompletedProcess(command, 1, "", error)

    with pytest.raises(checklib.PolicyError) as raised:
        checklib.authorize("p", "e", "a", "b", "c", {}, run=cedar)
    assert str(raised.value) == "failed to parse request; context `{}` is not valid"


def test_ask_reads_context_values() -> None:
    assert [ask.value_of(x) for x in ["yes", "No", "TRUE", "false"]] == [
        True,
        False,
        True,
        False,
    ]
    assert ask.value_of("120") == 120 and ask.value_of("-3") == -3
    assert ask.value_of("north") == "north"


def test_ask_says_what_it_needs(capsys) -> None:
    assert ask.main(["alice", "view"]) == 1
    assert "give a principal, an action and a resource" in capsys.readouterr().out
    assert ask.main(["--dir", str(ROOT / "nowhere"), "alice", "view", "o-1"]) == 1
    assert "there is no policies.cedar in" in capsys.readouterr().out
    assert ask.main(["--help"]) == 0
    assert capsys.readouterr().out.startswith("ask: may this principal")


# --- access-review ---------------------------------------------------------------


def day(text: str) -> datetime.date:
    return datetime.date.fromisoformat(text)


LOG = [
    (day("2026-07-10"), "reports", "export", "Order"),
    (day("2026-07-31"), "reports", "read", "Order"),
    (day("2026-09-14"), "backup", "delete", "Order"),
    (day("2026-10-28"), "reports", "read", "Order"),
]
GRANTED = [("read", "Order"), ("export", "Order"), ("delete", "Order")]


def test_the_window_is_counted_back_from_the_logs_newest_line() -> None:
    used, unused, first, newest = access_review.review(GRANTED, LOG, "reports", 90)
    # 90 days ending on 28 October begin on 31 July, which is inside.
    assert (first, newest) == (day("2026-07-31"), day("2026-10-28"))
    assert used == [("read", "Order", 2, day("2026-10-28"))]
    # The export of 10 July is outside; the delete was another principal's.
    assert unused == [("export", "Order"), ("delete", "Order")]
    used, unused, first, _ = access_review.review(GRANTED, LOG, "reports", 89)
    assert first == day("2026-08-01") and used[0][2] == 1
    used, unused, _, _ = access_review.review(GRANTED, LOG, "reports", 120)
    assert [(a, k) for a, k, _, _ in used] == [("read", "Order"), ("export", "Order")]
    assert unused == [("delete", "Order")]


def test_a_resources_kind_is_read_from_either_spelling() -> None:
    assert access_review.kind_of("Order/o-17") == "Order"
    assert access_review.kind_of('Order::"o-17"') == "Order"


def test_a_log_or_catalogue_line_out_of_shape_names_its_line(tmp_path) -> None:
    log = tmp_path / "access.log"
    log.write_text(
        "2026-07-10 reports read Order/o-1\n\nlast week reports read Order/o-2\n",
        encoding="utf-8",
    )
    with pytest.raises(checklib.PolicyError) as raised:
        access_review.read_log(str(log))
    assert "line 3: a log line is DATE PRINCIPAL ACTION RESOURCE" in str(raised.value)
    catalogue = tmp_path / "catalogue.txt"
    catalogue.write_text("# actions\nread Order\nexport\n", encoding="utf-8")
    with pytest.raises(checklib.PolicyError) as raised:
        access_review.read_catalogue(str(catalogue))
    assert "line 3: a catalogue line is ACTION RESOURCE-TYPE" in str(raised.value)
    catalogue.write_text("# actions\nread Order  # all of them\n", encoding="utf-8")
    assert access_review.read_catalogue(str(catalogue)) == [("read", "Order")]


def test_access_review_says_what_it_needs(capsys) -> None:
    assert access_review.main([]) == 1
    assert "name one principal" in capsys.readouterr().out
    assert access_review.main(["--days", "soon", "reports"]) == 1
    assert "--days takes a whole number of days" in capsys.readouterr().out
    assert access_review.main(["--dir", str(ROOT / "nowhere"), "reports"]) == 1
    assert "there is no file" in capsys.readouterr().out


# --- the files as Docker will copy them -------------------------------------------

SCRIPTS = [
    BASE / "checklib.py",
    BASE / "bin" / "ask",
    BASE / "bin" / "access-review",
    BASE / "bin" / "ca-whatif",
    ROOT / "content" / "lab-bases" / "tm" / "tm-check",
]


@pytest.mark.parametrize("script", SCRIPTS, ids=[s.name for s in SCRIPTS])
def test_a_base_script_is_python_312_with_unix_line_endings(script) -> None:
    # The lab image's Python is Ubuntu 24.04's 3.12, older than the one these
    # tests run on. "ruff format" at the repository's own target (3.14) once
    # rewrote "except (A, B):" as "except A, B:", which 3.12 refuses, and
    # every helper died at import: format these files with
    # --target-version py312.
    import ast

    data = script.read_bytes()
    assert b"\r" not in data
    ast.parse(data.decode("utf-8"), feature_version=(3, 12))
    if script.suffix != ".py":
        assert data.startswith(b"#!/usr/bin/python3\n")
