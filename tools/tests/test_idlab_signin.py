"""signin, the identity labs' scripted browser (content/lab-bases/id/bin/signin),
reading pages Keycloak really served.

signin finds its way by the ids of Keycloak's forms and the classes of its
messages. A Keycloak upgrade that renames one would break every identity
lab at once, in CI, minutes into each. These tests read the same pages from
files, so the break shows here first, in a second.

The pages in keycloak_pages/ were saved from Keycloak 26.8.2 on the base on
2026-11-22 (its login theme is Apache-2.0, like the rest of Keycloak). When
the pin in content/lab-bases/id/Dockerfile moves, save them again from the
new version and run these.
"""

from pathlib import Path

import pytest
from idlab_files import signin

PAGES = Path(__file__).parent / "keycloak_pages"


def page(name: str) -> str:
    return (PAGES / f"{name}.html").read_text(encoding="utf-8")


def form(name: str, form_id: str) -> dict:
    found = [f for f in signin.forms_of(page(name)) if f["id"] == form_id]
    assert len(found) == 1, f"{name}.html should have one form with id {form_id}"
    return found[0]


def test_the_sign_in_form() -> None:
    login = form("login", "kc-form-login")
    assert login["method"] == "post"
    assert {"username", "password"} <= set(login["inputs"])
    # The form posts to the provider's own address, with its session in it.
    assert login["action"].startswith(
        "https://login.shop.test/realms/shop/login-actions/authenticate?"
    )
    # "&amp;" in the page is "&" in the address the browser posts to.
    assert "&amp;" not in login["action"] and "&execution=" in login["action"]
    assert signin.page_message(page("login")) is None


def test_a_wrong_password_and_a_disabled_account_say_why() -> None:
    assert (
        signin.page_message(page("login-wrong-password"))
        == "Invalid username or password."
    )
    assert (
        signin.page_message(page("login-disabled"))
        == "Account is disabled, contact your administrator."
    )
    # Both show the sign-in form again, which is how signin knows it failed.
    form("login-wrong-password", "kc-form-login")
    form("login-disabled", "kc-form-login")


def test_the_one_time_code_form() -> None:
    otp = form("otp", "kc-otp-login-form")
    assert otp["method"] == "post" and "otp" in otp["inputs"]


def test_the_security_key_page() -> None:
    body = page("webauthn")
    webauth = form("webauthn", "webauth")
    # The fields the page's own script fills in from the key's answer.
    assert {
        "clientDataJSON",
        "authenticatorData",
        "signature",
        "credentialId",
        "userHandle",
        "error",
    } <= set(webauth["inputs"])
    assert signin.script_value(body, "rpId") == "login.shop.test"
    challenge = signin.script_value(body, "challenge")
    assert challenge and len(challenge) >= 16


def test_the_page_that_registers_a_security_key() -> None:
    body = page("webauthn-register")
    register = form("webauthn-register", "register")
    assert {
        "clientDataJSON",
        "attestationObject",
        "publicKeyCredentialId",
        "authenticatorLabel",
        "transports",
        "error",
    } <= set(register["inputs"])
    assert signin.script_value(body, "rpId") == "login.shop.test"
    assert signin.script_value(body, "challenge")
    assert signin.script_value(body, "userid")


def test_a_key_answer_from_the_wrong_origin_is_refused_in_keycloaks_words() -> None:
    assert (
        signin.page_message(page("webauthn-bad-origin")) == "Passkey origin mismatch."
    )


def test_the_error_page_for_a_redirect_address_nobody_registered() -> None:
    body = page("error-redirect")
    assert signin.page_message(body) == "Invalid parameter: redirect_uri"
    assert not any(
        f["id"] in ("kc-form-login", "kc-otp-login-form", "webauth", "register")
        for f in signin.forms_of(body)
    )


def test_the_device_code_page_and_a_wrong_code() -> None:
    code = form("device-code", "kc-user-verify-device-user-code-form")
    assert code["method"] == "post" and "device_user_code" in code["inputs"]
    # A path, not a whole address: signin joins it to the page's own.
    assert code["action"] == "/realms/shop/device"
    assert signin.page_message(page("device-code")) is None
    form("device-bad-code", "kc-user-verify-device-user-code-form")
    assert (
        signin.page_message(page("device-bad-code"))
        == "Invalid code, please try again."
    )


def test_the_consent_page() -> None:
    body = page("consent")
    consent = signin.consent_form(signin.forms_of(body))
    assert consent is not None and consent["method"] == "post"
    assert consent["action"].startswith("/realms/shop/login-actions/consent?")
    assert "code" in consent["inputs"]
    assert signin.page_title(body) == "Grant Access to The warehouse scanner"
    # No other page is taken for it.
    for other in ("login", "otp", "webauthn", "device-code", "error-redirect"):
        assert signin.consent_form(signin.forms_of(page(other))) is None, other


def test_the_page_after_a_device_is_approved() -> None:
    assert (
        signin.page_message(page("device-done"))
        == "You may close this browser window and go back to your device."
    )


# --- The parts that need no page ------------------------------------------------------


def test_one_time_codes_follow_rfc_6238() -> None:
    # RFC 6238's SHA-1 test key, the ASCII string "12345678901234567890",
    # in base32 as an authenticator app holds it; its eight-digit test
    # values end in these six digits.
    secret = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
    assert signin.totp(secret, at=59) == "287082"
    assert signin.totp(secret, at=1111111109) == "081804"
    assert signin.totp(secret, at=1234567890) == "005924"
    # Lowercase, as a person might paste it.
    assert signin.totp(secret.lower(), at=59) == "287082"


@pytest.mark.parametrize(
    ("rp_id", "origin", "allowed"),
    [
        ("login.shop.test", "https://login.shop.test", True),
        # A parent of the page's host is allowed (a key for shop.test works
        # on login.shop.test), a sibling or a lookalike is not.
        ("shop.test", "https://login.shop.test", True),
        ("login.shop.test", "https://login.shop-help.test", False),
        ("login.shop.test", "https://shop.test", False),
        ("shop.test", "https://evilshop.test", False),
        ("login.shop.test", "https://login.shop.test.evil.test", False),
    ],
)
def test_the_browsers_rule_for_which_site_may_ask_for_a_key(
    rp_id: str, origin: str, allowed: bool
) -> None:
    assert signin.browser_allows(rp_id, origin) is allowed


def test_long_values_are_cut_in_what_v_shows() -> None:
    long = "https://login.shop.test/auth?state=" + "a" * 80 + "&client_id=shop-web"
    assert signin.shorten(long) == (
        "https://login.shop.test/auth?state=" + "a" * 48 + "...&client_id=shop-web"
    )
