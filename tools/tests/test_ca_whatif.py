"""ca-whatif, the labs' model of Microsoft Entra Conditional Access
(content/lab-bases/policy/bin/ca-whatif), against the rules Microsoft's
documentation states, each worked out here by hand:

- "Multiple Conditional Access policies can apply ... all applicable
  policies must be satisfied"; "All assignments are logically combined using
  AND"; a block "stops here"; "By default, multiple controls require all";
  "Require one of the selected controls"; policies apply to all client app
  types when the condition isn't configured; phase 1 runs for enabled and
  report-only policies, phase 2 (enforcement) for enabled ones only
  (https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-policies,
  ms.date 2026-03-24, read 2026-11-22).
- The table of built-in authentication strengths
  (https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths,
  read 2026-11-22).
- An exclusion beats an inclusion, and emergency accounts are excluded
  through one group (the strong-authentication topic's brief, facts G8 and
  G15, from Microsoft's pages).

The strong-authentication topic's checks evaluate a learner's policy files
with it, so a wrong verdict here would pass wrong work. The identity base
carries a copy of the file; the last test fails if the two differ.
"""

import importlib.machinery
import importlib.util
import io
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CA_WHATIF = ROOT / "content" / "lab-bases" / "policy" / "bin" / "ca-whatif"


def load():
    loader = importlib.machinery.SourceFileLoader("ca_whatif", str(CA_WHATIF))
    spec = importlib.util.spec_from_loader("ca_whatif", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


ca = load()

DIRECTORY = {
    "users": [
        {"id": "alice", "groups": ["staff"], "roles": []},
        {"id": "carol", "groups": ["staff", "partner-admins"], "roles": []},
        {"id": "dan", "groups": ["contractors"], "roles": []},
        {"id": "gail", "groups": ["staff"], "roles": ["Global Administrator"]},
        {
            "id": "bg-1",
            "groups": ["emergency-access"],
            "roles": ["Global Administrator"],
        },
    ],
    "groups": ["staff", "contractors", "partner-admins", "emergency-access"],
    "roles": ["Global Administrator"],
    "apps": ["portal", "admin-app"],
}
LOCATIONS = [
    {"displayName": "warehouse", "isTrusted": True},
    {"displayName": "cafe", "isTrusted": False},
]
EVERYONE = {"includeUsers": ["All"]}
ALL_APPS = {"includeApplications": ["All"]}


def policy(name="p", state="enabled", users=None, apps=None, grant=None, **conditions):
    """A policy in Graph's shape; grant is a list of controls (AND), or a
    dict for anything else."""
    if isinstance(grant, list) or grant is None:
        grant = {"operator": "AND", "builtInControls": grant or ["mfa"]}
    return {
        "displayName": name,
        "state": state,
        "conditions": {
            "users": users or EVERYONE,
            "applications": apps or ALL_APPS,
            **conditions,
        },
        "grantControls": grant,
    }


def strength(name):
    return {"operator": "OR", "authenticationStrength": {"displayName": name}}


class World:
    """A folder with a directory, locations and policy files, and ca-whatif
    run on it."""

    def __init__(self, folder: Path, policies: dict):
        self.folder = folder
        (folder / "policies").mkdir()
        (folder / "directory.json").write_text(json.dumps(DIRECTORY), encoding="utf-8")
        (folder / "locations.json").write_text(json.dumps(LOCATIONS), encoding="utf-8")
        for name, value in policies.items():
            text = value if isinstance(value, str) else json.dumps(value)
            (folder / "policies" / name).write_text(text, encoding="utf-8")
        self.options = [
            "--policies",
            str(folder / "policies"),
            "--directory",
            str(folder / "directory.json"),
            "--locations",
            str(folder / "locations.json"),
        ]

    def run(self, *args, stdin=None):
        return ca.run([*self.options, *args], stdin)

    def batch(self, *sign_ins):
        text, status = self.run("--batch", stdin=io.StringIO(json.dumps(sign_ins)))
        assert status == 0, text
        return json.loads(text)

    def one(self, user="alice", app="portal", **signals):
        return self.batch({"user": user, "app": app, **signals})[0]

    def result(self, user="alice", app="portal", **signals):
        verdict = self.one(user, app, **signals)
        return verdict["result"], verdict["why"]

    def rows(self, user="alice", app="portal", **signals):
        return {
            row["file"]: row["outcome"]
            + (f" ({row['reason']})" if "reason" in row else "")
            for row in self.one(user, app, **signals)["policies"]
        }


@pytest.fixture
def world(tmp_path):
    return lambda policies: World(tmp_path, policies)


# --- which policies apply --------------------------------------------------------


def test_with_no_policy_everything_is_allowed(world) -> None:
    assert world({}).result(methods="pwd") == ("allow", "")


def test_a_policy_includes_by_name_group_or_role(world) -> None:
    w = world(
        {
            "1-name.json": policy(users={"includeUsers": ["dan"]}),
            "2-group.json": policy(users={"includeGroups": ["partner-admins"]}),
            "3-role.json": policy(users={"includeRoles": ["Global Administrator"]}),
        }
    )
    applied = {
        user: [f for f, outcome in w.rows(user).items() if outcome == "applied"]
        for user in ["alice", "dan", "carol", "gail"]
    }
    assert applied == {
        "alice": [],
        "dan": ["1-name.json"],
        "carol": ["2-group.json"],
        "gail": ["3-role.json"],
    }
    assert w.rows("alice")["1-name.json"] == "not applied (users)"


def test_an_exclusion_beats_an_inclusion(world) -> None:
    w = world(
        {
            "1.json": policy(
                users={"includeUsers": ["All"], "excludeGroups": ["emergency-access"]},
                grant=["block"],
            ),
            "2.json": policy(
                users={
                    "includeRoles": ["Global Administrator"],
                    "excludeUsers": ["bg-1"],
                },
                grant=["block"],
            ),
            "3.json": policy(
                users={
                    "includeGroups": ["staff"],
                    "excludeRoles": ["Global Administrator"],
                },
                grant=["block"],
            ),
        }
    )
    assert w.result("bg-1") == ("allow", "")
    assert set(w.rows("bg-1").values()) == {
        "not applied (the user is excluded)",
        "not applied (users)",
    }
    # gail is staff and a Global Administrator: policy 3 excludes her role,
    # policies 1 and 2 still apply.
    assert w.rows("gail") == {
        "1.json": "applied",
        "2.json": "applied",
        "3.json": "not applied (the user is excluded)",
    }


def test_the_first_condition_that_doesnt_match_is_the_reason(world) -> None:
    everything = policy(
        users={"includeGroups": ["staff"]},
        apps={"includeApplications": ["portal"]},
        clientAppTypes=["browser"],
        signInRiskLevels=["high"],
        userRiskLevels=["high"],
        locations={"includeLocations": ["cafe"]},
    )
    w = world({"p.json": everything})
    match = {
        "user": "alice",
        "app": "portal",
        "client": "browser",
        "risk": "high",
        "userrisk": "high",
        "location": "cafe",
    }
    assert w.batch(match)[0]["policies"][0]["outcome"] == "applied"
    # Break each condition, later ones first: the reason is always the
    # earliest condition that fails, in Entra's order of assignments.
    broken = dict(match)
    for key, value, reason in [
        ("location", "warehouse", "location"),
        ("userrisk", "low", "user risk"),
        ("risk", "medium", "sign-in risk"),
        ("client", "other", "client app"),
        ("app", "admin-app", "applications"),
        ("user", "dan", "users"),
    ]:
        broken[key] = value
        row = w.batch(broken)[0]["policies"][0]
        assert (row["outcome"], row["reason"]) == ("not applied", reason), key


def test_a_condition_a_policy_doesnt_set_matches_everything(world) -> None:
    w = world({"p.json": policy(grant=["block"])})
    for signals in [
        {"client": "exchangeActiveSync"},
        {"client": "mobileAppsAndDesktopClients", "risk": "high"},
        {"location": "cafe", "userrisk": "medium", "device": "compliant"},
    ]:
        assert w.result(**signals)[0] == "block", signals


def test_legacy_authentication_is_two_client_types(world) -> None:
    w = world(
        {
            "p.json": policy(
                clientAppTypes=["exchangeActiveSync", "other"], grant=["block"]
            )
        }
    )
    blocked = {
        client: w.result(client=client)[0] == "block"
        for client in [
            "browser",
            "mobileAppsAndDesktopClients",
            "exchangeActiveSync",
            "other",
        ]
    }
    assert blocked == {
        "browser": False,
        "mobileAppsAndDesktopClients": False,
        "exchangeActiveSync": True,
        "other": True,
    }
    w = world_again(w, {"p.json": policy(clientAppTypes=["all"], grant=["block"])})
    assert w.result(client="browser")[0] == "block"


def world_again(old: World, policies: dict) -> World:
    """The same folder with other policy files."""
    for file in (old.folder / "policies").iterdir():
        file.unlink()
    (old.folder / "policies").rmdir()
    return World(old.folder, policies)


def test_applications_include_and_exclude(world) -> None:
    w = world(
        {
            "p.json": policy(
                apps={
                    "includeApplications": ["All"],
                    "excludeApplications": ["portal"],
                },
                grant=["block"],
            )
        }
    )
    assert w.result(app="admin-app")[0] == "block"
    assert w.rows(app="portal") == {
        "p.json": "not applied (the application is excluded)"
    }


def test_locations_all_named_and_trusted(world) -> None:
    # "Only from the trusted warehouse": block everywhere except trusted
    # places, the usual way to write it.
    w = world(
        {
            "p.json": policy(
                users={"includeGroups": ["contractors"]},
                locations={
                    "includeLocations": ["All"],
                    "excludeLocations": ["AllTrusted"],
                },
                grant=["block"],
            )
        }
    )
    assert w.result("dan", location="warehouse") == ("allow", "")
    assert w.result("dan", location="cafe")[0] == "block"
    assert w.result("dan")[0] == "block"  # no named location at all
    assert w.rows("dan", location="warehouse") == {
        "p.json": "not applied (the location is excluded)"
    }
    w = world_again(
        w,
        {
            "p.json": policy(
                locations={"includeLocations": ["AllTrusted"]}, grant=["block"]
            )
        },
    )
    assert w.result(location="warehouse")[0] == "block"
    assert w.rows(location="cafe") == {"p.json": "not applied (location)"}
    assert w.rows() == {"p.json": "not applied (location)"}


# --- what the policies that apply demand -------------------------------------------


def test_a_block_wins_over_everything_satisfied(world) -> None:
    w = world(
        {
            "1-mfa.json": policy(),
            "2-block.json": policy(signInRiskLevels=["high"], grant=["block"]),
        }
    )
    assert w.result(methods="pwd,otp") == ("allow", "")
    assert w.result(methods="pwd,hwk", risk="high", device="compliant") == (
        "block",
        "blocked by 2-block.json",
    )


def test_every_policy_that_applies_must_be_satisfied(world) -> None:
    # Microsoft's own example: one policy asks for MFA and another for a
    # compliant device, so the sign-in needs both.
    w = world(
        {
            "1-mfa.json": policy(),
            "2-device.json": policy(grant=["compliantDevice"]),
        }
    )
    assert w.result(methods="pwd,otp", device="compliant") == ("allow", "")
    assert w.one(methods="pwd,otp", device="compliant")["controls"] == [
        "mfa",
        "compliantDevice",
    ]
    assert w.result(methods="pwd,otp") == (
        "block",
        "can't sign in with compliantDevice",
    )
    assert w.result(methods="pwd", device="compliant") == (
        "block",
        "can't sign in with mfa",
    )
    assert w.result(methods="pwd") == (
        "block",
        "can't sign in with mfa and compliantDevice",
    )


def test_and_needs_all_of_a_policys_controls_and_or_needs_one(world) -> None:
    both = {"operator": "AND", "builtInControls": ["mfa", "compliantDevice"]}
    either = {"operator": "OR", "builtInControls": ["mfa", "compliantDevice"]}
    w = world({"p.json": policy(grant=both)})
    assert w.result(methods="pwd,otp")[0] == "block"
    assert w.result(methods="pwd", device="compliant")[0] == "block"
    assert w.result(methods="pwd,otp", device="compliant")[0] == "allow"
    w = world_again(w, {"p.json": policy(grant=either)})
    assert w.result(methods="pwd,otp")[0] == "allow"
    assert w.result(methods="pwd", device="compliant")[0] == "allow"
    assert w.result(methods="pwd") == (
        "block",
        "can't sign in with mfa and compliantDevice",
    )


def test_report_only_is_worked_out_and_never_enforced(world) -> None:
    w = world(
        {
            "1-block.json": policy(
                state="enabledForReportingButNotEnforced", grant=["block"]
            ),
            "2-device.json": policy(
                state="enabledForReportingButNotEnforced", grant=["compliantDevice"]
            ),
        }
    )
    assert w.result(methods="pwd") == ("allow", "")
    assert w.rows() == {"1-block.json": "report-only", "2-device.json": "report-only"}
    assert w.one()["controls"] == []
    text, status = w.run("alice", "portal", "device=compliant")
    assert status == 0
    assert "(report-only) would have applied: blocks. Report-only: Failure" in text
    assert (
        "(report-only) would have applied: requires compliantDevice: satisfied. "
        "Report-only: Success" in text
    )


def test_a_disabled_policy_is_skipped(world) -> None:
    w = world({"p.json": policy(state="disabled", grant=["block"])})
    assert w.result() == ("allow", "")
    assert w.rows() == {"p.json": "disabled"}


# Microsoft's table: which ways of signing in satisfy which built-in strength.
#   methods                       MFA    passwordless  phishing-resistant
STRENGTH_TABLE = [
    ("hwk", True, True, True),  # FIDO2 security key
    ("whfb", True, True, True),  # Windows Hello for Business
    ("cert", True, True, True),  # certificate-based (multifactor)
    ("phone", True, True, False),  # Authenticator phone sign-in
    ("tap", True, False, False),  # Temporary Access Pass
    ("pwd,otp", True, False, False),  # a password plus something you have
    ("pwd,sms", True, False, False),
    ("pwd,voice", True, False, False),
    ("pwd,push", True, False, False),
    ("pwd,hwk", True, True, True),
    ("pwd", False, False, False),
    ("sms", False, False, False),
    ("otp", False, False, False),  # something you have, and nothing else
    ("otp,sms", False, False, False),  # two of the same kind of factor
]


@pytest.mark.parametrize("row", STRENGTH_TABLE, ids=[r[0] for r in STRENGTH_TABLE])
def test_authentication_strengths_follow_microsofts_table(world, row) -> None:
    methods, mfa, passwordless, phishing_resistant = row
    w = world(
        {
            "1.json": policy(users={"includeUsers": ["alice"]}, grant=["mfa"]),
            "2.json": policy(
                users={"includeUsers": ["dan"]},
                grant=strength("Multifactor authentication"),
            ),
            "3.json": policy(
                users={"includeUsers": ["carol"]}, grant=strength("Passwordless MFA")
            ),
            "4.json": policy(
                users={"includeUsers": ["gail"]},
                grant=strength("Phishing-resistant MFA"),
            ),
        }
    )
    got = [
        w.result(user, methods=methods)[0] == "allow"
        for user in ["alice", "dan", "carol", "gail"]
    ]
    assert got == [mfa, mfa, passwordless, phishing_resistant]


def test_the_briefs_two_sign_ins_read_as_designed(world) -> None:
    w = world(
        {
            "10-everyone-mfa.json": policy("Everyone: MFA"),
            "20-admins.json": policy(
                "Admins: phishing-resistant",
                users={"includeGroups": ["partner-admins"]},
                grant=strength("Phishing-resistant MFA"),
            ),
        }
    )
    text, status = w.run("carol", "admin-app", "methods=pwd,otp")
    assert status == 0
    assert text.splitlines() == [
        "sign-in: carol to admin-app  (methods pwd,otp; risk none; user risk none; "
        "device unknown; location none; client browser)",
        "result: block (can't sign in with phishingResistant)",
        "policies:",
        "  10-everyone-mfa.json  applied: requires mfa: satisfied",
        "  20-admins.json        applied: requires phishingResistant: not satisfied",
    ]
    text, _ = w.run("carol", "admin-app", "methods=pwd,key")  # an alias of hwk
    assert text.splitlines()[1] == "result: allow after mfa, phishingResistant"
    text, _ = w.run("alice", "portal", "methods=pwd,otp", "risk=low")
    assert text.splitlines()[1] == "result: allow after mfa"
    assert text.splitlines()[4] == "  20-admins.json        not applied (users)"


# --- the command line ----------------------------------------------------------------


def test_a_sign_in_that_names_nobody_or_nothing_known_is_refused(world) -> None:
    w = world({"p.json": policy()})
    assert w.run("alise", "portal") == (
        'ca-whatif: there is no user "alise" (did you mean "alice"?)',
        1,
    )
    assert w.run("alice", "portl")[0] == (
        'ca-whatif: there is no app "portl" (did you mean "portal"?)'
    )
    assert w.run("alice")[0].startswith("ca-whatif: give a user and an app")
    assert w.run("alice", "portal", "methods=pwd,pin")[0].startswith(
        'ca-whatif: "pin" is not a sign-in method: the methods are pwd, otp'
    )
    assert w.run("alice", "portal", "risk=severe")[0] == (
        'ca-whatif: risk is one of none, low, medium, high, not "severe"'
    )
    assert w.run("alice", "portal", "mood=good")[0].startswith(
        'ca-whatif: "mood" is not a signal'
    )
    assert w.run("alice", "portal", "location=moon")[0] == (
        'ca-whatif: there is no named location "moon"'
    )
    assert w.run("alice", "portal", "--loud")[1] == 1
    text, status = ca.run(["--help"])
    assert status == 0 and text.startswith("ca-whatif: what would these")


def test_batch_takes_made_up_people_from_the_directory_it_is_given(
    world, tmp_path
) -> None:
    # A check adds its own people to a copy of the directory and asks about
    # hundreds of sign-ins in one process.
    w = world(
        {"p.json": policy(users={"includeGroups": ["contractors"]}, grant=["block"])}
    )
    directory = json.loads(json.dumps(DIRECTORY))
    directory["users"].append(
        {"id": "user-3f9a2c", "groups": ["contractors"], "roles": []}
    )
    copy = tmp_path / "copy.json"
    copy.write_text(json.dumps(directory), encoding="utf-8")
    w.options[3] = str(copy)
    sign_ins = [
        {"user": "user-3f9a2c", "app": "portal"},
        {"user": "alice", "app": "portal"},
    ]
    sign_ins += [{"user": "alice", "app": "portal", "methods": ["pwd", "otp"]}] * 300
    verdicts = w.batch(*sign_ins)
    assert [v["result"] for v in verdicts[:2]] == ["block", "allow"]
    assert len(verdicts) == 302


def test_people_groups_roles_and_apps_come_from_a_keycloak_realm_file(
    world, tmp_path
) -> None:
    realm = {
        "realm": "shop",
        "users": [
            {"username": "alice", "groups": ["/staff"], "realmRoles": ["admin"]},
            {"username": "ben", "groups": ["/staff/warehouse"]},
        ],
        "groups": [{"name": "staff"}, {"name": "emergency-access"}],
        "roles": {"realm": [{"name": "admin"}, {"name": "auditor"}]},
        "clients": [{"clientId": "portal"}, {"clientId": "admin-app"}],
    }
    assert ca.directory_from_realm(realm) == {
        "users": {
            "alice": {"groups": {"staff"}, "roles": {"admin"}},
            "ben": {"groups": {"warehouse"}, "roles": set()},
        },
        "groups": {"staff", "emergency-access", "warehouse"},
        "roles": {"admin", "auditor"},
        "apps": {"portal", "admin-app"},
    }
    w = world({"p.json": policy(users={"includeRoles": ["admin"]}, grant=["block"])})
    file = tmp_path / "shop.json"
    file.write_text(json.dumps(realm), encoding="utf-8")
    options = ["--policies", w.options[1], "--realm", str(file)]
    text, status = ca.run([*options, "alice", "portal"])
    assert status == 0 and "result: block (blocked by p.json)" in text
    text, status = ca.run([*options, "ben", "portal"])
    assert status == 0 and "result: allow" in text


def test_it_finds_its_files_in_the_current_folder(world, monkeypatch) -> None:
    w = world({"p.json": policy(grant=["block"])})
    monkeypatch.chdir(w.folder)
    text, status = ca.run(["alice", "portal"])
    assert status == 0 and "result: block" in text
    assert ca.run(["--lint"]) == ("ok", 0)


def test_with_no_files_anywhere_it_says_where_to_run_it(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    text, status = ca.run(["alice", "portal"])
    if not Path("/etc/shop/ca").is_dir():
        assert status == 1
        assert text.startswith("ca-whatif: there are no policies here: run it in")


# --- --lint: a typo is an error -----------------------------------------------------

BAD_FILES = [
    ("{", "isn't valid JSON"),
    (
        policy(grantControl=1) | {"grantControl": {}},
        'the policy has no property "grantControl" (did you mean "grantControls"?)',
    ),
    (
        policy(state="on"),
        '"state" is one of enabled, disabled, enabledForReportingButNotEnforced, '
        'and this one says "on"',
    ),
    (policy(name=""), 'it needs a "displayName", the policy\'s name'),
    (
        policy(users={"includeGroup": ["staff"]}),
        '"users" has no property "includeGroup" (did you mean "includeGroups"?)',
    ),
    (
        policy(users={"includeGroups": ["staf"]}),
        '"includeGroups" names "staf", and there is no such group '
        '(did you mean "staff"?)',
    ),
    (
        policy(users={"includeRoles": ["Global Admin"]}),
        '"includeRoles" names "Global Admin", and there is no such role',
    ),
    (
        policy(users={"includeUsers": ["all"]}),
        '"includeUsers" names "all", and there is no such user',
    ),
    (policy(users={"excludeGroups": ["staff"]}), '"users" includes nobody'),
    (
        policy(apps={"includeApplications": ["portl"]}),
        '"includeApplications" names "portl", and there is no such app '
        '(did you mean "portal"?)',
    ),
    (
        policy(signInRiskLevels=["severe"]),
        '"signInRiskLevels" names "severe", and there is no such risk level',
    ),
    (
        policy(clientAppTypes=["legacy"]),
        '"clientAppTypes" names "legacy", and there is no such client app type',
    ),
    (
        policy(locations={"includeLocations": ["moon"]}),
        '"includeLocations" names "moon", and there is no such named location',
    ),
    (
        policy(devices={"deviceFilter": {}}),
        '"conditions" has no property "devices"',
    ),
    (
        policy(grant=["mfa", "block"]),
        "a policy that blocks can't also ask for controls",
    ),
    (policy(grant=["2fa"]), 'there is no control "2fa" (did you mean "mfa"?)'),
    (
        policy(grant=["domainJoinedDevice"]),
        'the control "domainJoinedDevice" exists in Entra and is not part of',
    ),
    (
        policy(grant={"operator": "ALL", "builtInControls": ["mfa"]}),
        '"operator" is AND or OR, and this one says "ALL"',
    ),
    (
        policy(grant={"operator": "OR", "builtInControls": []}),
        '"grantControls" asks for nothing',
    ),
    (
        policy(grant=strength("Phishing resistant")),
        '"authenticationStrength" is {"displayName": ...} with Multifactor '
        "authentication, Passwordless MFA or Phishing-resistant MFA",
    ),
    (
        policy(
            grant={
                "operator": "AND",
                "builtInControls": ["mfa"],
                "authenticationStrength": {"displayName": "Passwordless MFA"},
            }
        ),
        '"mfa" and "authenticationStrength" can\'t be in one policy',
    ),
    ([policy()], "the policy should be an object, in braces"),
]


@pytest.mark.parametrize("case", BAD_FILES, ids=[c[1][:50] for c in BAD_FILES])
def test_lint_names_the_file_and_what_is_wrong(world, case) -> None:
    bad, expected = case
    w = world({"10-good.json": policy(), "20-bad.json": bad})
    text, status = w.run("--lint")
    assert status == 1
    assert text.startswith("20-bad.json"), text
    assert expected in text, text
    assert "10-good.json" not in text
    # A sign-in isn't decided on files that aren't well formed.
    text, status = w.run("alice", "portal")
    assert status == 1
    assert text.startswith("ca-whatif: a policy file isn't well formed. 20-bad.json")


def test_lint_is_ok_for_every_shape_the_model_knows(world) -> None:
    full = policy(
        users={
            "includeUsers": ["None"],
            "excludeUsers": ["dan"],
            "includeGroups": ["staff"],
            "excludeGroups": ["emergency-access"],
            "includeRoles": ["Global Administrator"],
            "excludeRoles": [],
        },
        apps={"includeApplications": ["portal"], "excludeApplications": ["admin-app"]},
        clientAppTypes=["all"],
        signInRiskLevels=["medium", "high"],
        userRiskLevels=["none", "low"],
        locations={
            "includeLocations": ["All"],
            "excludeLocations": ["AllTrusted", "cafe"],
        },
        grant=strength("Passwordless MFA"),
    )
    full["id"] = "f2b6"
    w = world(
        {"a.json": full, "b.json": policy(grant=["block"]), "notes.txt": "ignored"}
    )
    assert w.run("--lint") == ("ok", 0)


def test_the_identity_bases_copy_is_this_file() -> None:
    # The plan gives ca-whatif one source, here, and a byte-identical copy in
    # the identity base (MODULE-4-BRIEF.md, 4.1, row 7).
    copies = sorted((ROOT / "content" / "lab-bases").glob("id/**/ca-whatif"))
    if not copies:
        pytest.skip("the identity base isn't in this checkout yet")
    for copy in copies:
        assert copy.read_bytes() == CA_WHATIF.read_bytes(), copy
