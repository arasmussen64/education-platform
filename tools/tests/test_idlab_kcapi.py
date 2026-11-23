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
