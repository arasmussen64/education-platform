# The policy lab base

Every lab that has a learner write access rules as code (the Cloud Solutions Architect track's `csa.sec.authn-authz`, and the conditional-access write lab of `csa.sec.strong-auth`) starts `FROM lab-base-policy`. This folder is that image. `tools/labcheck.py` builds it, tagged `lab-base-policy`, before it builds any lab whose `Dockerfile` says `FROM lab-base-policy`, for `start` and `test` alike ([ADR-0018](../../../docs/decisions/0018-lab-checker-local-mode.md), third amendment).

Read this before writing a policy lab. The plan behind it is [docs/plans/cloud-module-4/MODULE-4-BRIEF.md](../../../docs/plans/cloud-module-4/MODULE-4-BRIEF.md), section 4.4, with the two topics' briefs (authentication and authorization, sections 7 and 10; strong authentication, section 7.6).

## What's in the image

| Layer | What | Notes |
| --- | --- | --- |
| 1 | Module 3's plain labs' first `RUN`, byte for byte | Shared with every plain lab of Module 3 on, so Docker builds it once. Change it only with all of them. |
| 2 | `ca-certificates`, `xz-utils`, and the Cedar command-line tool as `/usr/local/bin/cedar` | The one download from outside Ubuntu's archive, pinned below. Its licence files are in `/usr/share/doc/cedar/`. |
| 3 | `ask`, `access-review`, `ca-whatif` in `/usr/local/bin`; `checklib.py` in `/usr/local/lib/policy/` | Python, standard library only, on Ubuntu 24.04's Python 3.12. |

It is a plain base: no systemd, no network, no privilege. It ends with `USER learner`, `WORKDIR /home/learner` and `CMD ["sleep", "infinity"]`. Not in it: OPA and Rego (Cedar is this module's policy language; Rego waits for Module 18), and `jq` (checks read JSON with `python3`).

### The pin

| | |
| --- | --- |
| What | Cedar CLI (`cedar-policy-cli`), the policy language's reference command-line tool |
| Version | 4.14.1, released 2026-11-02. The newest release at least two weeks old on 2026-11-22, when the base was built: 4.15.0 came out on 2026-11-16 |
| Licence | Apache-2.0 (the archive's `LICENSE`; `NOTICE` says "Copyright Cedar Contributors") |
| From | `https://github.com/cedar-policy/cedar/releases/download/cedar-policy-cli-v4.14.1/cedar-policy-cli-ARCH-unknown-linux-gnu.tar.xz` |
| sha256, x86_64 | `5833e9f4734eac0d95b3dab7ae119a9212caf0a82e02720b989e2fce6f3bfdad` |
| sha256, aarch64 | `499cfb6a6a7eab28ceca7b24215525a2d107fbf3faca759318a253d485b7d346` |

Both checksums were computed from the downloaded archives on 2026-11-22 and equal the release's own `.sha256` files. The `Dockerfile` checks the archive before unpacking it and picks the build for the machine's processor; the x86_64 one is the one that has been built and run (CI and the owner's PC), the aarch64 one is there for an ARM laptop and is untried. To move the pin, change the version and both checksums in the `Dockerfile` and this table, rebuild, and run the tests and the probe lab: the helpers read the tool's printed words (below).

## A lab's folder and Dockerfile

```text
exercises/<lab>/
├── exercise.yaml      runtime: lab, lab: { restart_trial: true }
├── Dockerfile         below
├── <story>/           the schema, entities.json, and the learner's policies.cedar
├── <story>-cases      the lab's own case generator, on checklib (below)
├── checks.yaml        one rule a check
├── solution.sh        writes the policies, as the learner would type them
└── wrong/*.sh         each writes policies that are wrong in one way
```

```dockerfile
FROM lab-base-policy
USER root
COPY shop/ /home/learner/shop/
COPY --chmod=755 shop-cases /usr/local/lib/lab-checks/shop-cases
RUN chmod -R a+rX,go-w /home/learner/shop \
 && chown learner:learner /home/learner/shop /home/learner/shop/policies.cedar \
 && sha256sum /home/learner/shop/shop.cedarschema /home/learner/shop/entities.json > /usr/local/lib/lab-checks/shop.sha256
USER learner
```

The base ends as the learner, so a lab's own lines run between `USER root` and `USER learner`. `restart_trial: true` passes trivially (the policies are a file), and every lab still sets it. The probe lab `csa.sec.plain-probes/probe-refund-rules` is the pattern until the topic's own labs exist.

One trap, met while building this: `COPY --chmod=644 file /new/folder/file` gives the **folder** it creates mode 644 as well, which nobody but root can enter. Copy into a folder and set modes in a `RUN`, as the base's own `Dockerfile` does.

## Cedar, as the pinned tool behaves

Run on 2026-11-22, in the image:

- `cedar validate --schema S --policies P` ends with status 0, or 3 with the policy, the line and a suggestion (`attribute `stor` on entity type `Staff` not found ... did you mean `store`?`).
- `cedar authorize` ends with status 0 for `ALLOW`, 2 for `DENY` and 1 when it couldn't decide (a request the schema refuses, policies that don't parse). With `-v` it lists the policies that decided: the permits for an allow, the forbids for a deny, and nothing for a default deny. A policy named with `@id("...")` is listed by that name, any other as `policy0`, `policy1`, ... in the file's order.
- **Without a schema, a policy that fails while it is evaluated is skipped**, silently for the decision: `principal.stor` makes the permit never apply. That is why every lab has a `validates` check and its other checks pass the schema.
- `cedar run-tests --policies P --tests T.json` takes a JSON list of tests, each with `request` (`principal`, `action` and `resource` as strings such as `Staff::"alice"`, and `context`), its own `entities`, `decision`, `reason` and `num_errors`; it refuses a test without the last two. It prints `test NAME ... ok`, or `fail: expected Deny, got Allow`, or `error:` with a reason. **Each test carries its own entities**, which is what lets every case have people nobody has seen. 500 tests took 0.07 s, and 0.14 s with a schema.
- With `--schema`, `run-tests` validates the policies before each test, so policies the schema refuses make every test an `error`. `checklib` reports that as the learner's ("the policies don't validate against the schema ..."), not as a broken check.
- `-f plain` gives error text without box-drawing characters; the helpers use it everywhere.

## checklib.py: checks that make up their requests

A check on a learner's policies must not be passable by a policy that names this lab's people, stores or amounts. So a check **makes up its requests when it runs**: every combination of a rule's cases, new random names for every principal, resource and store in every run, and both sides of every number in a rule. The designer's two findings behind this: with store names drawn from a list of eight, a policy that named one store passed 1 run in 4; with one amount drawn at random from 100 and 101, `< 100` for `<= 100` passed whenever 101 came up.

A lab writes its own small generator on the library (the probe's `shop-cases` is the pattern) and each check runs it for one rule:

```text
#!/usr/bin/python3
import sys
sys.path.insert(0, "/usr/local/lib/policy")
from checklib import Case, Names, check, combine, entity, ref, sides, uid

names = Names()
cases = []
for c in combine(same_store=[True, False], amount=sides(100)):
    store, other = names.new("store"), names.new("store")
    clerk, order = names.new("staff"), names.new("order")
    cases.append(Case(
        words=f"support staff, {'their own' if c['same_store'] else 'another'} store, "
              f"refunding an order of {c['amount']}",
        principal=uid("Staff", clerk), action=uid("Action", "refund"),
        resource=uid("Order", order), context={"mfa": True},
        entities=[entity("Role", "support"),
                  entity("Staff", clerk, {"store": store}, [("Role", "support")]),
                  entity("Order", order, {"store": store if c["same_store"] else other,
                                          "amount": c["amount"]})],
        allow=c["same_store"] and c["amount"] <= 100))
check("/home/learner/shop/policies.cedar", cases, schema="/home/learner/shop/shop.cedarschema")
```

| Name | What it does |
| --- | --- |
| `Names()`, `.new(kind)` | `staff-3f9a2c`: new in every run, never repeated within one, hex after the kind so it never starts with `-` and never needs quoting. |
| `combine(**dimensions)` | Every combination of the named dimensions' values, each as a dict. |
| `sides(limit)` | The numbers that try "up to LIMIT": the limit and the number just past it, **always both**, with one well below and one well above that change from run to run (so `== 100` fails too). |
| `Case(words, principal, action, resource, entities, allow, context)` | One request, the entities that exist while it is asked, what the rules say, and how to say the case to a learner. |
| `uid`, `ref`, `entity` | `Staff::"alice"`; an entity as an attribute's value; an entity for a case's list, with `(kind, name)` parents. |
| `check(policies, cases, schema)` | Prints `ok`, or the first three cases that disagree and how many more, and ends with status 0, so a check is `expect: { equals: ok }`. All cases go to one `cedar run-tests`. Only the decision is compared: which policy decided is the learner's business. |
| `decide`, `disagreements`, `report` | The steps of `check`, for a lab that needs them apart. |
| `validates(schema, policies)` | `ok`, or Cedar's first reason. |
| `find_entity`, `load_entities`, `authorize` | What `ask` and `access-review` share. |

A disagreement reads as the case's own words: `support staff, their own store, refund on an order of 100 that a colleague handled, with MFA: the rules say allow, your policy says deny`. Write `words` so that sentence tells the learner which rule to read again, and nothing about how to write it.

## Rules for checks and labs on the base

- **One rule a check**, so a failure points at one skill. Each check runs the lab's generator for one rule.
- **Both decisions in every check.** A check whose cases are all "deny" passes on an empty file, and one whose cases are all "allow" passes `permit (principal, action, resource);`. Where a rule is only a denial (default deny), another check must demand the allows.
- **Vary what a rule doesn't mention.** A rule about refunds says nothing of viewing: the view cases still run with and without MFA, on both sides of the refund limit, on one's own orders and a colleague's. The probe's first version held those fixed, and two wrong policies passed (a limit on viewing; a forbid written for every action). Each is a `wrong/*.sh` now.
- **A `wrong/*.sh` for each likely mistake**: a missing forbid, a name or a store written into the policy, the wrong side of a limit, an unconstrained `principal`, a misspelt attribute, a forbid too wide.
- **A `validates` check, and the schema passed to every other.**
- **The schema and `entities.json` are the system as it is**: read-only, with a checksum check, and the prompt says to change only the policies.
- **`ask` in a check is fine as an end state on the lab's own people** ("Alice may refund order o-1002 with MFA"), never as the only proof of a rule.
- **Edit the helpers for Python 3.12** and format them with `ruff format --target-version py312`: at the repository's own target, ruff once rewrote `except (A, B):` in a form 3.12 refuses, and every helper died at import. A test parses every base script as 3.12.

## ask

```text
ask [-v] [--dir FOLDER] PRINCIPAL ACTION RESOURCE [KEY=VALUE ...]

$ ask alice refund o-1004 mfa=yes
DENY
  decided by no-refund-of-your-own-order
```

One request through `cedar authorize`, for a learner who is writing policies. It reads `policies.cedar`, `entities.json` and the folder's one `*.cedarschema` from the current folder. Names are looked up in `entities.json` (`alice` for `Staff::"alice"`; a name two kinds share must be written in full). `KEY=VALUE` pairs are the request's context: `yes`, `no`, `true` and `false` are Booleans, digits a number, anything else text; **a Boolean the schema asks for and the learner leaves out counts as no**. It prints `ALLOW` or `DENY`, then the deciding policies, or `no policy applies, and what no permit allows is denied`; `-v` adds each deciding policy's kind and the request as Cedar got it. It ends with status 0 for either answer and 1 when it couldn't ask (no such person, no such action, policies that don't parse), with one sentence.

## access-review

```text
access-review [--days N] [--dir FOLDER] [--log FILE] PRINCIPAL
```

Scenery for the least-privilege lab: a stand-in for the clouds' analyzers, **modelled on IAM Access Analyzer's unused access findings and Google's role recommendations, and neither of them**; a page that shows it says so. It reads, in the folder, `policies.cedar`, `entities.json` and `catalogue.txt` (every action there is, one `ACTION RESOURCE-TYPE` a line), and an access log of `DATE PRINCIPAL ACTION RESOURCE` lines (`2026-08-04 reports read Order/o-17`): `--log FILE`, or the path in the folder's `log` file, or `/var/log/ops/access.log`.

For each catalogue line it asks Cedar whether the principal may do that action to a resource of that type (the first entity of the type in `entities.json`, with an empty context and no schema), then looks for such a request in the last N days of the log. **The window is counted back from the log's newest line**, not from today, so a lab's constructed log gives the same answer on any day. It prints two lists, `granted and used` and `granted, never used in N days`, and nothing about what happened before the window: that a quarterly job is missing from 90 days of log is the lab's lesson.

## ca-whatif

```text
ca-whatif USER APP [SIGNAL=VALUE ...]     one sign-in, in words
ca-whatif --lint                          are the policy files well formed?
ca-whatif --batch < sign-ins.json         many sign-ins, as JSON, for checks
```

A model of Microsoft Entra Conditional Access **as its documentation describes it**: not Entra, and not its What If tool; every page that shows it says so. It has one source, here, and a byte-identical copy in the identity base (`tools/tests/test_ca_whatif.py` fails when they differ), where it reads people from Keycloak's realm file.

Policies are JSON files in Microsoft Graph's `conditionalAccessPolicy` shape, one a file, read in name order: `displayName`, `state` (`enabled`, `disabled`, `enabledForReportingButNotEnforced`), `conditions` (`users` with `includeUsers`, `excludeUsers`, `includeGroups`, `excludeGroups`, `includeRoles`, `excludeRoles`; `applications` with `includeApplications`, `excludeApplications`; `clientAppTypes`; `signInRiskLevels`; `userRiskLevels`; `locations` with `includeLocations`, `excludeLocations`), and `grantControls` (`operator` `AND` or `OR`; `builtInControls` from `block`, `mfa`, `compliantDevice`; `authenticationStrength` as `{"displayName": ...}` with one of Microsoft's three built-in names). Graph's other controls and conditions (`domainJoinedDevice`, device filters, platforms, session controls) are refused by name rather than ignored, so a policy never seems to pass by accident.

It decides in two passes, as Microsoft's "Building a Conditional Access policy" describes (read 2026-11-22):

1. **Which policies apply.** Every condition a policy sets must match; one it doesn't set matches everything (so a policy with no `clientAppTypes` applies to every client). A user is included by name, group or role, and **an exclusion beats an inclusion**. The first condition that doesn't match, in the order users, applications, client app, sign-in risk, user risk, location, is the reason shown for "not applied".
2. **What they demand.** If any policy that applies blocks, the sign-in is blocked. Otherwise **every** policy that applies must be satisfied: all of its controls (`AND`) or one of them (`OR`).

A report-only policy is worked out and shown (`Report-only: Failure` or `Success`) and never changes the result; a disabled one is skipped. Which sign-in methods satisfy which strength follows Microsoft's table of built-in strengths (read 2026-11-22): a FIDO2 key (`hwk`), Windows Hello (`whfb`) or a multifactor certificate (`cert`) satisfies all three; Authenticator phone sign-in (`phone`) is MFA and passwordless; a Temporary Access Pass (`tap`), or a password with something the person has (`otp`, `sms`, `voice`, `push`), is MFA only; a password alone, or two things of one kind, is nothing.

**Where it reads**, unless told with `--policies DIR`, `--directory FILE` (or `--realm FILE`) and `--locations FILE`: `./policies/`, `./directory.json` and `./locations.json` when the current folder has them; else `~/ca/` the same way; else `/etc/shop/ca/` with the people, groups, realm roles and clients of `/etc/keycloak/realms/shop.json`. `directory.json` is `{"users": [{"id", "groups", "roles"}], "groups": [...], "roles": [...], "apps": [...]}`; the locations file is a list of `{"displayName", "isTrusted"}`.

**`--lint`** prints `ok`, or one line a problem, each starting with the file's name, and ends with status 1: a property that doesn't exist (with "did you mean"), a group, role, user, app or location the directory doesn't have, a state or operator that isn't one, a block beside other controls, `mfa` beside an authentication strength (Entra refuses the pair). A sign-in isn't decided while a file isn't well formed: a typo is an error, as a misspelt attribute is with Cedar's schema.

**`--batch`** reads a JSON list of sign-ins (`{"user", "app", "methods": [...], "risk", "userrisk", "device", "location", "client"}`) from standard input and prints a JSON list of verdicts (`result`, `why`, `controls`, and each policy's row), hundreds in one process. A check that needs made-up people writes a copy of the directory with them added and passes `--directory`; a user the directory doesn't know belongs to no group.

## What the tests hold

- `tools/tests/test_policy_checklib.py`: `sides` always has both sides of the limit; names never repeat; the reference rules agree on 576 generated cases and each of ten wrong policies disagrees in every run; only the decision is compared; a disagreement is said in the case's words, three at most; policies that don't parse, policies the schema refuses and a case Cedar refuses are each told apart; `authorize` reads the pinned tool's printed words; `access-review`'s window. Cedar isn't on the machine those tests run on, so a stand-in answers in the tool's words; **the real tool is exercised by the probe lab's contract**.
- `tools/tests/test_ca_whatif.py`: the rules above one by one, Microsoft's strength table row by row, 22 kinds of malformed file, the realm file, the batch mode.

## Size and time

On the owner's PC (Docker Desktop 29.8.2, 2026-11-22): the image is 297 MB as Docker reports it (Ubuntu with Python and curl, the 18.6 MB `cedar`, `ca-certificates` and `xz-utils`); the Cedar layer builds in 9 s once the first layer is cached, and the base in a second or two after that. A rule check of 96 generated cases takes about 0.2 s, most of it Python starting; a lab container holds under 1 MiB of memory. The probe lab's contract (pristine, solution, restart trial, eight wrong fixes: eleven containers) took 51 s and 79 s in two runs, with other work on the machine both times. Nothing here has run on a GitHub runner yet: the probe lab is how it will, and the one thing to read there is the download from GitHub's release during the build.

## Files here

| File | What |
| --- | --- |
| `Dockerfile` | The three layers and the pin. |
| `checklib.py` | The checks' library. |
| `bin/ask`, `bin/access-review` | The learner's helpers for Cedar labs. |
| `bin/ca-whatif` | The conditional-access model. One source: the identity base's copy must equal it. |
| `README.md` | This file. |
