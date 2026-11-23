"""kcapi, the identity labs' way into Keycloak's admin API
(content/lab-bases/id/lib/kcapi.py): the parts that decide something and
need no server.

`realm-saved` (kc_saved in checks) says "saved" when the running realm
equals a fresh build of its file. It compares two exports of Keycloak's
after `normal` has taken out what differs between any two builds, and
reports what `differences` finds. If either is wrong, a change made only in
the console passes, or an untouched realm fails. `kc-flows` and `idp-user`
are checked for the lines and the person they build.
"""

import json
from pathlib import Path

import pytest
from idlab_files import kcapi


def test_normal_drops_ids_and_sorts_so_two_builds_compare_equal() -> None:
    live = {
        "id": "aaa",
        "realm": "shop",
        "clients": [
            {"id": "1", "clientId": "shop-web", "redirectUris": ["b", "a"]},
            {"id": "2", "clientId": "account", "containerId": "aaa"},
        ],
    }
    fresh = {
        "id": "bbb",
        "realm": "chk-shop",
        "clients": [
            {"id": "9", "clientId": "account", "containerId": "bbb"},
            {"id": "8", "clientId": "shop-web", "redirectUris": ["a", "b"]},
        ],
    }
    assert kcapi.normal(live, False) == kcapi.normal(fresh, True)


def test_normal_takes_the_copys_name_out_of_the_copy_only() -> None:
    # The throwaway copy is the realm chk-shop, and Keycloak writes that
    # name into addresses and role names. Only the copy is rewritten: a
    # live realm that really says "chk-" somewhere still shows as different.
    fresh = {"baseUrl": "/realms/chk-shop/account/"}
    assert kcapi.normal(fresh, True) == {"baseUrl": "/realms/shop/account/"}
    assert kcapi.normal(fresh, False) == fresh


def test_normal_leaves_out_the_keys_keycloak_makes_for_itself() -> None:
    components = [
        {"name": "fallback-RS256", "providerId": "rsa-generated"},
        {"name": "2026", "providerId": "rsa"},
    ]
    assert kcapi.normal(components, False) == [{"name": "2026", "providerId": "rsa"}]


def test_no_differences_between_equal_exports() -> None:
    realm = {"realm": "shop", "clients": [{"clientId": "shop-web", "enabled": True}]}
    assert kcapi.differences(realm, json.loads(json.dumps(realm))) == []


def test_a_changed_setting_is_named_by_its_path() -> None:
    live = {"clients": [{"clientId": "shop-web", "redirectUris": ["https://a/*"]}]}
    fresh = {"clients": [{"clientId": "shop-web", "redirectUris": ["https://a/cb"]}]}
    assert kcapi.differences(live, fresh) == [
        (".clients[shop-web].redirectUris", ["https://a/*"], ["https://a/cb"])
    ]


def test_something_added_or_removed_in_the_console_is_named() -> None:
    live = {"clients": [{"clientId": "shop-web"}, {"clientId": "extra"}]}
    fresh = {"clients": [{"clientId": "shop-web"}, {"clientId": "account"}]}
    assert kcapi.differences(live, fresh) == [
        (".clients[account]", "(not there)", "there"),
        (".clients[extra]", "there", "(not there)"),
    ]


def test_a_setting_on_one_side_only_is_a_difference() -> None:
    live = {"accessTokenLifespan": 3600}
    assert kcapi.differences(live, {}) == [(".accessTokenLifespan", 3600, "(not set)")]
    assert kcapi.differences({}, live) == [(".accessTokenLifespan", "(not set)", 3600)]


def test_a_flow_steps_requirement_is_found_inside_its_flow() -> None:
    # What the strong-authentication labs turn on: a step switched from
    # DISABLED to ALTERNATIVE through the admin API, the file untouched.
    def flows(requirement: str) -> dict:
        return {
            "authenticationFlows": [
                {
                    "alias": "Browser - Conditional 2FA",
                    "authenticationExecutions": [
                        {
                            "authenticator": "auth-otp-form",
                            "requirement": "ALTERNATIVE",
                        },
                        {
                            "authenticator": "webauthn-authenticator",
                            "requirement": requirement,
                        },
                    ],
                }
            ]
        }

    assert kcapi.differences(flows("ALTERNATIVE"), flows("DISABLED")) == [
        (
            ".authenticationFlows[Browser - Conditional 2FA]"
            ".authenticationExecutions[webauthn-authenticator].requirement",
            "ALTERNATIVE",
            "DISABLED",
        )
    ]


def test_a_list_without_names_is_compared_whole() -> None:
    assert kcapi.differences({"scopes": ["a", "b"]}, {"scopes": ["a"]}) == [
        (".scopes", ["a", "b"], ["a"])
    ]


def test_a_value_of_another_type_is_a_difference() -> None:
    assert kcapi.differences({"x": "1"}, {"x": 1}) == [(".x", "1", 1)]


# --- kc-flows -------------------------------------------------------------------------

FILE_REALM = {
    "browserFlow": "shop browser",
    "authenticationFlows": [
        {
            "alias": "shop browser",
            "authenticationExecutions": [
                {
                    "authenticator": "auth-cookie",
                    "requirement": "ALTERNATIVE",
                    "priority": 10,
                },
                {
                    "flowAlias": "shop forms",
                    "authenticatorFlow": True,
                    "requirement": "ALTERNATIVE",
                    "priority": 20,
                },
            ],
        },
        {
            "alias": "shop forms",
            "authenticationExecutions": [
                # Out of order in the file: priority decides.
                {
                    "authenticator": "webauthn-authenticator",
                    "requirement": "REQUIRED",
                    "priority": 30,
                },
                {
                    "authenticator": "conditional-user-role",
                    "requirement": "REQUIRED",
                    "priority": 20,
                    "authenticatorConfig": "admins",
                },
                {
                    "authenticator": "auth-username-password-form",
                    "requirement": "REQUIRED",
                    "priority": 10,
                },
            ],
        },
    ],
    "authenticatorConfig": [{"alias": "admins", "config": {"condUserRole": "admin"}}],
}


def test_a_flow_in_a_realm_file_is_shown_as_a_tree() -> None:
    assert kcapi.flow_lines_from_file(FILE_REALM, "shop browser") == [
        "ALTERNATIVE auth-cookie",
        "ALTERNATIVE shop forms  (a sub-flow: its steps are indented below)",
        "  REQUIRED    auth-username-password-form",
        "  REQUIRED    conditional-user-role  [condUserRole=admin]",
        "  REQUIRED    webauthn-authenticator",
    ]


def test_a_flow_the_file_doesnt_define_is_none() -> None:
    assert kcapi.flow_lines_from_file({}, "browser") is None
    assert kcapi.flow_lines_from_file(FILE_REALM, "browser") is None


def test_a_sub_flow_missing_from_the_file_says_so() -> None:
    realm = {
        "authenticationFlows": [
            {
                "alias": "top",
                "authenticationExecutions": [
                    {
                        "flowAlias": "gone",
                        "authenticatorFlow": True,
                        "requirement": "REQUIRED",
                    }
                ],
            }
        ]
    }
    assert kcapi.flow_lines_from_file(realm, "top") == [
        "REQUIRED    gone  (a sub-flow: its steps are indented below)",
        "  ?           (not in the file)",
    ]


def test_the_servers_list_of_steps_is_shown_the_same_way() -> None:
    # As GET /authentication/flows/browser/executions answers (26.8.2).
    executions = [
        {"providerId": "auth-cookie", "requirement": "ALTERNATIVE", "level": 0},
        {
            "displayName": "forms",
            "authenticationFlow": True,
            "requirement": "ALTERNATIVE",
            "level": 0,
        },
        {
            "providerId": "conditional-credential",
            "requirement": "REQUIRED",
            "level": 1,
            "authenticationConfig": "c1",
        },
    ]
    configs = {"c1": {"credentials": "webauthn-passwordless"}}
    assert kcapi.flow_lines_from_server(executions, configs.get) == [
        "ALTERNATIVE auth-cookie",
        "ALTERNATIVE forms  (a sub-flow: its steps are indented below)",
        "  REQUIRED    conditional-credential  [credentials=webauthn-passwordless]",
    ]


# --- idp-user -------------------------------------------------------------------------


def test_a_checks_person_has_what_keycloaks_profile_check_asks_for() -> None:
    person = kcapi.person("chk-u1", "pw", ["staff"], "id-1")
    assert person["username"] == "chk-u1" and person["id"] == "id-1"
    assert person["enabled"] and person["emailVerified"]
    assert person["firstName"] and person["lastName"] and person["email"]
    assert person["groups"] == ["/staff"]
    assert person["credentials"] == [
        {"type": "password", "value": "pw", "temporary": False}
    ]


def test_a_person_with_an_app_and_a_key_has_three_credentials() -> None:
    person = kcapi.person("chk-u1", "pw", [], "id-1", "5ec2e7", '{"credentialId":"x"}')
    kinds = [c["type"] for c in person["credentials"]]
    assert kinds == ["password", "otp", "webauthn"]
    otp = person["credentials"][1]
    assert json.loads(otp["secretData"]) == {"value": "5ec2e7"}
    # Keycloak's defaults for an authenticator app, which signin's codes follow.
    assert json.loads(otp["credentialData"]) == {
        "subType": "totp",
        "digits": 6,
        "counter": 0,
        "period": 30,
        "algorithm": "HmacSHA1",
    }
    assert person["credentials"][2]["credentialData"] == '{"credentialId":"x"}'


# --- realm-saved on what Keycloak really exports --------------------------------------
#
# keycloak_exports/one-of-each.json is what realm-saved read from Keycloak
# 26.8.2 on the base (2026-11-23), for a realm that was just applied and so
# is saved: the export of the running realm, the export of the throwaway
# copy built from the same file, and each one's client secrets. The realm
# has one of each kind of client the base supports: a site with a secret
# (shop-web), public clients (trace-cli, and scanner with the device
# grant), two with a service account and a secret (job, job2), one that
# signs in with a signed token instead of a secret (signed-job), a
# bearer-only API (stock-api), a SAML client, and an identity provider.
# People with a password, an authenticator app and a security key were in
# the realm's file; an export lists no people. Every real secret was
# replaced by a made-up one before the file was saved: "the-file's-..."
# where the realm had the file's value, "made-by-keycloak-..." where the
# file gives none and Keycloak made one.
#
# Save it again when the pin moves: in a lab whose realm file has those
# clients and people, after "sudo realm-apply", run Python on idp that
# imports /usr/local/lib/idlab/kcapi.py and writes, as JSON,
#   "filed": file_secrets(read_realm("shop")),
#   "live":  {"export": export("shop"), "secrets": client_secrets("shop")},
#   "fresh": the same two for "chk-shop", between build_copy("shop", data)
#            and the copy's removal,
# with every secret replaced as above. Then read what
# test_what_is_left_out_is_exactly_what_keycloak_stamps reports: a field
# the new Keycloak stamps shows there first.

EXPORTS = Path(__file__).parent / "keycloak_exports" / "one-of-each.json"


def one_of_each() -> dict:
    return json.loads(EXPORTS.read_text(encoding="utf-8"))


def compared(saved: dict) -> list:
    """What realm-saved finds between the two halves of the saved file."""
    filed = saved["filed"]
    live, fresh = saved["live"], saved["fresh"]
    return kcapi.differences(
        kcapi.comparable(live["export"], False, live["secrets"], filed),
        kcapi.comparable(fresh["export"], True, fresh["secrets"], filed),
    )


def by_name(items: list, name: str) -> dict:
    return next(item for item in items if kcapi.name_of(item) == name)


def test_the_saved_exports_hold_one_of_each_kind() -> None:
    live = one_of_each()["live"]["export"]
    clients = {c["clientId"]: c for c in live["clients"]}
    assert clients["https://app.shop.test/hr"]["protocol"] == "saml"
    assert clients["job"]["serviceAccountsEnabled"]
    assert clients["signed-job"]["clientAuthenticatorType"] == "client-jwt"
    assert clients["stock-api"]["bearerOnly"]
    assert clients["trace-cli"]["publicClient"]
    assert [u["username"] for u in live["users"]] == [
        "service-account-job",
        "service-account-job2",
        "service-account-signed-job",
    ]
    assert [p["alias"] for p in live["identityProviders"]] == ["partners"]


def test_a_realm_with_a_service_account_and_a_saml_client_is_saved() -> None:
    assert compared(one_of_each()) == []


def test_what_is_left_out_is_exactly_what_keycloak_stamps(monkeypatch) -> None:
    # With nothing but ids left out, the two builds of one file differ in
    # these settings and in no other. Each is a moment or an id Keycloak
    # made for itself: the README says why each is safe to leave out.
    assert kcapi.STAMPED == (
        "createdTimestamp",
        "client.secret.creation.time",
        "internalId",
    )
    monkeypatch.setattr(kcapi, "DROPPED", ("id", "containerId", "subComponents"))
    paths = {path for path, _, _ in compared(one_of_each())}
    assert paths == {
        ".clients[https://app.shop.test/hr].attributes.client.secret.creation.time",
        ".clients[signed-job].attributes.client.secret.creation.time",
        ".clients[stock-api].attributes.client.secret.creation.time",
        ".identityProviders[partners].internalId",
        ".users[service-account-job].createdTimestamp",
        ".users[service-account-job2].createdTimestamp",
        ".users[service-account-signed-job].createdTimestamp",
    }


# Each change below is one a learner (or a hurried fix) can make in the
# running realm alone, through the admin API. Each was made that way on the
# base, and realm-saved named it; here the same change is made to the saved
# export of the running realm.


def wildcard_redirect(live: dict) -> None:
    client = by_name(live["export"]["clients"], "shop-web")
    client["redirectUris"] = ["https://app.shop.test/*"]


def another_secret(live: dict) -> None:
    live["secrets"]["shop-web"] = "typed-into-the-console"


def another_audience(live: dict) -> None:
    client = by_name(live["export"]["clients"], "shop-web")
    mapper = by_name(client["protocolMappers"], "stock-api-audience")
    mapper["config"]["included.custom.audience"] = "https://other.shop.test"


def a_new_role(live: dict) -> None:
    live["export"]["roles"]["realm"].append({"name": "auditor", "composite": False})


def a_service_account_in_another_group(live: dict) -> None:
    by_name(live["export"]["users"], "service-account-job")["groups"].append("/staff")


def a_service_account_with_another_role(live: dict) -> None:
    account = by_name(live["export"]["users"], "service-account-job")
    account["realmRoles"].append("offline_access")


def a_service_account_switched_off(live: dict) -> None:
    by_name(live["export"]["users"], "service-account-job2")["enabled"] = False


def a_flow_step_switched_off(live: dict) -> None:
    flow = by_name(live["export"]["authenticationFlows"], "browser")
    step = by_name(flow["authenticationExecutions"], "identity-provider-redirector")
    step["requirement"] = "DISABLED"


def a_client_made_in_the_console(live: dict) -> None:
    live["export"]["clients"].append({"clientId": "extra", "publicClient": True})


def longer_tokens(live: dict) -> None:
    live["export"]["accessTokenLifespan"] = 3600


def saml_assertions_unsigned(live: dict) -> None:
    client = by_name(live["export"]["clients"], "https://app.shop.test/hr")
    client["attributes"]["saml.assertion.signature"] = "false"


def the_password_grant_switched_on(live: dict) -> None:
    by_name(live["export"]["clients"], "job")["directAccessGrantsEnabled"] = True


def another_identity_provider_address(live: dict) -> None:
    provider = by_name(live["export"]["identityProviders"], "partners")
    provider["config"]["issuer"] = "https://login.shop-help.test/realms/partners"


REAL_DIFFERENCES = [
    (wildcard_redirect, ".clients[shop-web].redirectUris"),
    (another_secret, ".clients[shop-web].secret"),
    (
        another_audience,
        ".clients[shop-web].protocolMappers[stock-api-audience]"
        ".config.included.custom.audience",
    ),
    (a_new_role, ".roles.realm[auditor]"),
    (a_service_account_in_another_group, ".users[service-account-job].groups"),
    (a_service_account_with_another_role, ".users[service-account-job].realmRoles"),
    (a_service_account_switched_off, ".users[service-account-job2].enabled"),
    (
        a_flow_step_switched_off,
        ".authenticationFlows[browser]"
        ".authenticationExecutions[identity-provider-redirector].requirement",
    ),
    (a_client_made_in_the_console, ".clients[extra]"),
    (longer_tokens, ".accessTokenLifespan"),
    (
        saml_assertions_unsigned,
        ".clients[https://app.shop.test/hr].attributes.saml.assertion.signature",
    ),
    (the_password_grant_switched_on, ".clients[job].directAccessGrantsEnabled"),
    (another_identity_provider_address, ".identityProviders[partners].config.issuer"),
]


@pytest.mark.parametrize(
    ("change", "path"), REAL_DIFFERENCES, ids=[c.__name__ for c, _ in REAL_DIFFERENCES]
)
def test_a_real_difference_is_still_caught(change, path: str) -> None:
    saved = one_of_each()
    change(saved["live"])
    assert [found for found, _, _ in compared(saved)] == [path]


def test_a_changed_secret_is_named_and_never_printed() -> None:
    saved = one_of_each()
    another_secret(saved["live"])
    [(path, now, file)] = compared(saved)
    assert (now, file) == ("(not the file's secret)", "(the file's secret)")
    assert kcapi.shown(path, now) == '"(not the file\'s secret)"'
    # Any other setting whose name says "secret" is hidden as well: the
    # old secret Keycloak keeps while a rotation runs, say.
    rotated = ".clients[shop-web].attributes.client.secret.rotated"
    assert kcapi.shown(rotated, "0ld-s3cret") == '"(a secret, not shown)"'
    assert kcapi.shown(rotated, "(not set)") == '"(not set)"'
    assert kcapi.shown(".clients[secret-shop].enabled", True) == "true"


def test_a_secret_the_file_doesnt_give_is_not_compared() -> None:
    # A SAML client, a bearer-only API and a client that signs its own
    # tokens get a secret Keycloak makes up, new in every build. It is no
    # setting of the file's, so two different ones are no difference.
    saved = one_of_each()
    name = "https://app.shop.test/hr"
    assert name not in saved["filed"]
    assert saved["live"]["secrets"][name] != saved["fresh"]["secrets"][name]
    assert compared(saved) == []


def test_people_are_not_compared_and_service_accounts_are() -> None:
    # Checks and provisioning make and change people while a lab runs
    # (federation's HR connector moves the file's own people between
    # groups), so a person is never a difference. Keycloak 26.8.2 exports
    # no people anyway; this holds if a later one does.
    saved = one_of_each()
    saved["live"]["export"]["users"].append({"username": "chk-u1", "enabled": True})
    assert compared(saved) == []
    saved["live"]["export"]["users"].append(
        {"username": "service-account-extra", "serviceAccountClientId": "extra"}
    )
    assert [path for path, _, _ in compared(saved)] == [".users[service-account-extra]"]


def test_the_files_secrets_are_the_clients_that_have_one() -> None:
    data = {
        "clients": [
            {"clientId": "shop-web", "secret": "s1"},
            {"clientId": "trace-cli", "publicClient": True},
        ]
    }
    assert kcapi.file_secrets(data) == {"shop-web": "s1"}
    assert kcapi.file_secrets({}) == {}


def test_a_sub_flow_among_a_flows_steps_is_named_too() -> None:
    def flow(requirement: str) -> dict:
        return {
            "authenticationFlows": [
                {
                    "alias": "browser",
                    "authenticationExecutions": [
                        {"authenticator": "auth-cookie", "requirement": "ALTERNATIVE"},
                        {"flowAlias": "forms", "requirement": requirement},
                    ],
                }
            ]
        }

    assert kcapi.differences(flow("REQUIRED"), flow("ALTERNATIVE")) == [
        (
            ".authenticationFlows[browser].authenticationExecutions[forms].requirement",
            "REQUIRED",
            "ALTERNATIVE",
        )
    ]


# --- A realm file that can't be applied -----------------------------------------------

GOOD_FILE = """{
  "realm": "shop",
  "enabled": true,
  "accessTokenLifespan": 300,
  "clients": [
    { "clientId": "shop-web", "secret": "${SHOP_WEB_SECRET}" }
  ]
}
"""


@pytest.fixture
def etc(tmp_path, monkeypatch):
    """An /etc/keycloak of the test's own: realms/shop.json and secrets.env."""
    (tmp_path / "realms").mkdir()
    (tmp_path / "realms" / "shop.json").write_text(GOOD_FILE, encoding="utf-8")
    (tmp_path / "secrets.env").write_text("SHOP_WEB_SECRET=s3cret\n", encoding="utf-8")
    monkeypatch.setattr(kcapi, "ETC", tmp_path.as_posix())
    monkeypatch.setattr(kcapi, "APPLIED", (tmp_path / "applied").as_posix())
    return tmp_path


def write_realm(etc: Path, text: str, realm: str = "shop") -> str:
    path = etc / "realms" / f"{realm}.json"
    path.write_text(text, encoding="utf-8")
    return path.as_posix()


def test_a_good_file_is_read_with_its_secrets_filled_in(etc: Path) -> None:
    data = kcapi.read_realm("shop")
    assert data["clients"][0]["secret"] == "s3cret"


def test_a_gap_is_refused_with_the_file_and_the_line(etc: Path) -> None:
    path = write_realm(etc, GOOD_FILE.replace("300", '"..."'))
    with pytest.raises(kcapi.FileProblem) as refused:
        kcapi.read_realm("shop")
    assert str(refused.value) == (
        f'{path}, line 4: a gap ("...") is still to be filled in'
    )


def test_invalid_json_is_refused_with_the_file_and_the_line(etc: Path) -> None:
    path = write_realm(etc, GOOD_FILE.replace('"enabled": true,', '"enabled": true'))
    with pytest.raises(kcapi.FileProblem) as refused:
        kcapi.read_realm("shop")
    # Python finds the slip where the next setting begins.
    assert str(refused.value) == (
        f"{path}, line 4: not valid JSON: Expecting ',' delimiter"
    )


def test_a_name_with_no_value_is_refused_with_the_line_and_the_name(etc: Path) -> None:
    path = write_realm(etc, GOOD_FILE.replace("SHOP_WEB_SECRET", "SHOP_WEB_SECRT"))
    with pytest.raises(kcapi.FileProblem) as refused:
        kcapi.read_realm("shop")
    assert str(refused.value) == (
        f"{path}, line 6: ${{SHOP_WEB_SECRT}} is not in {etc.as_posix()}/secrets.env"
    )


@pytest.mark.parametrize(
    "text",
    ["", "[]", GOOD_FILE.replace('"shop"', '"store"')],
    ids=["empty", "a list", "another realm's name"],
)
def test_a_file_that_is_no_realm_of_that_name_is_refused(etc: Path, text: str) -> None:
    write_realm(etc, text)
    with pytest.raises(kcapi.FileProblem, match="shop.json"):
        kcapi.read_realm("shop")


def test_a_file_problem_ends_a_command_with_its_message() -> None:
    # Typed by hand (sudo realm-apply), a refusal is one line on standard
    # error and exit status 1: what sys.exit(text) does.
    problem = kcapi.FileProblem("shop.json, line 4: a gap")
    assert isinstance(problem, SystemExit)
    assert problem.code == "shop.json, line 4: a gap"


class FakeKeycloak:
    """Stands in for kcapi.call: keeps the realms it holds, refuses to make
    one whose name is in `refuses`, and records every request."""

    def __init__(self, realms: set, refuses: tuple = ()) -> None:
        self.realms, self.refuses, self.asked = set(realms), refuses, []

    def __call__(self, method, url, body=None, form=None, token=None):
        path = url.split("/admin/realms", 1)[1]
        made = f" {body['realm']}" if body else ""
        self.asked.append(f"{method} {path or '/'}{made}")
        if method == "POST" and path == "":
            if body["realm"] in self.refuses:
                return 400, json.dumps({"errorMessage": "Invalid mapper"}).encode()
            self.realms.add(body["realm"])
            return 201, b""
        name = path.lstrip("/")
        if method == "DELETE":
            self.realms.discard(name)
            return 204, b""
        return (200, b"{}") if name in self.realms else (404, b"{}")


@pytest.fixture
def keycloak(monkeypatch):
    def use(fake: FakeKeycloak) -> FakeKeycloak:
        monkeypatch.setattr(kcapi, "call", fake)
        monkeypatch.setattr(kcapi, "_token", "a-token")
        monkeypatch.setattr(kcapi, "BASE", "https://login.shop.test")
        return fake

    return use


def test_apply_tries_the_file_in_a_copy_before_it_touches_the_realm(
    etc: Path, keycloak, capsys
) -> None:
    fake = keycloak(FakeKeycloak({"shop"}))
    kcapi.apply("shop")
    assert fake.asked == [
        "GET /shop",
        "DELETE /chk-shop",
        "POST / chk-shop",
        "DELETE /chk-shop",
        "DELETE /shop",
        "POST / shop",
    ]
    assert fake.realms == {"shop"}
    assert not kcapi.changed("shop")
    assert "realm shop rebuilt" in capsys.readouterr().out


def test_a_file_keycloak_refuses_leaves_the_running_realm_alone(
    etc: Path, keycloak
) -> None:
    fake = keycloak(FakeKeycloak({"shop"}, refuses=("chk-shop",)))
    with pytest.raises(kcapi.FileProblem) as refused:
        kcapi.apply("shop")
    assert str(refused.value) == (
        f"{etc.as_posix()}/realms/shop.json: Keycloak refused it (400): Invalid mapper"
    )
    assert "DELETE /shop" not in fake.asked
    assert fake.realms == {"shop"}  # the realm is there, the copy is gone
    assert kcapi.changed("shop")  # so the next start tries the file again


def test_a_file_with_a_gap_never_reaches_keycloak(etc: Path, keycloak) -> None:
    fake = keycloak(FakeKeycloak({"shop"}))
    write_realm(etc, GOOD_FILE.replace("300", '"..."'))
    with pytest.raises(kcapi.FileProblem):
        kcapi.apply("shop")
    assert fake.asked == []


def test_a_realm_that_isnt_there_yet_is_built_without_a_copy(
    etc: Path, keycloak
) -> None:
    # At image build (idlab bake) there is nothing to protect.
    fake = keycloak(FakeKeycloak(set()))
    kcapi.apply("shop")
    assert fake.asked == ["GET /shop", "POST / shop"]


def test_at_a_start_a_bad_file_is_reported_and_the_others_are_applied(
    etc: Path, keycloak, capsys, monkeypatch
) -> None:
    # What kc-wait runs once Keycloak answers. shop's file has a gap;
    # partners' is new and fine. One line names the file, the line and
    # what to type; partners is built; the status says a file was left.
    monkeypatch.delenv("JOURNAL_STREAM", raising=False)
    fake = keycloak(FakeKeycloak({"shop"}))
    path = write_realm(etc, GOOD_FILE.replace("300", '"..."'))
    write_realm(etc, '{ "realm": "partners" }', "partners")
    assert kcapi.apply_changed() == 3
    assert fake.realms == {"shop", "partners"}
    said = capsys.readouterr()
    assert said.err == (
        f'keycloak: {path}, line 4: a gap ("...") is still to be filled in. '
        "Realm shop was not rebuilt: Keycloak serves it as it was before the "
        "file changed. Mend the file, then: sudo realm-apply shop\n"
    )
    assert "realm partners rebuilt" in said.out
    # Mended, the next start applies it, and then there is nothing to do.
    write_realm(etc, GOOD_FILE)
    assert kcapi.apply_changed() == 0
    fake.asked.clear()
    assert kcapi.apply_changed() == 0
    assert fake.asked == []
    assert capsys.readouterr().err == ""


def test_in_the_journal_the_report_is_a_warning(
    etc: Path, keycloak, capsys, monkeypatch
) -> None:
    # systemd reads "<4>" at the start of a unit's line as "warning", so
    # journalctl -u keycloak@idp -p warning finds it.
    monkeypatch.setenv("JOURNAL_STREAM", "8:12345")
    keycloak(FakeKeycloak(set()))
    write_realm(etc, "{")
    assert kcapi.apply_changed() == 3
    err = capsys.readouterr().err
    assert err.startswith("<4>keycloak: ") and err.count("\n") == 1
    # The realm was never built, so nothing is served under its name.
    assert "There is no realm shop. Mend the file, then: sudo realm-apply shop" in err


def test_keycloaks_own_reason_is_read_from_its_log() -> None:
    # A person in a group that isn't there gets "unknown_error" from the
    # admin API; the reason is a line in Keycloak's log (26.8.2).
    log = (
        "2026-11-23 07:35:54,958 INFO  [org.keycloak.events] (executor-thread-1) x\n"
        "2026-11-23 07:37:49,786 ERROR [org.keycloak.services.error."
        "KeycloakErrorHandler] (executor-thread-1) Uncaught server error: "
        "java.lang.RuntimeException: Unable to find group specified by path: "
        "/no-such-group\n"
        "\tat org.keycloak.models.utils.RepresentationToModel.createGroups\n"
    )
    assert kcapi.reason_in(log) == (
        "Unable to find group specified by path: /no-such-group"
    )
    assert kcapi.reason_in("nothing went wrong\n") == ""
