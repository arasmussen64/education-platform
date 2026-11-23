"""jwtlib, the identity labs' token checker (content/lab-bases/id/lib/jwtlib.py).

`jwt verify`, the stock API and the checks all take its verdict, so a wrong
verdict here would pass wrong work in every identity lab. Each test builds
a real RS256 token with a key made on the spot and changes one thing.

The key is made here in plain Python (two primes from a seeded generator),
so the tests need nothing installed and no key sits in the repository.
"""

import json
import random

import pytest
from idlab_files import jwtlib

ISSUER = "https://login.shop.test/realms/shop"
AUDIENCE = "https://api.shop.test"
NOW = 1_800_000_000


def is_prime(n: int, rng: random.Random) -> bool:
    """Miller-Rabin, twenty rounds: plenty for a test key."""
    if n < 2 or n % 2 == 0:
        return n == 2
    for small in (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % small == 0:
            return n == small
    d, r = n - 1, 0
    while d % 2 == 0:
        d, r = d // 2, r + 1
    for _ in range(20):
        x = pow(rng.randrange(2, n - 1), d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def prime(bits: int, rng: random.Random) -> int:
    while True:
        candidate = rng.getrandbits(bits) | (3 << (bits - 2)) | 1
        if is_prime(candidate, rng):
            return candidate


def make_key(seed: int, bits: int = 2048) -> tuple[int, int, int]:
    """(n, e, d) of an RSA key. Seeded, so every run makes the same one."""
    rng = random.Random(seed)
    e = 65537
    while True:
        p, q = prime(bits // 2, rng), prime(bits // 2, rng)
        phi = (p - 1) * (q - 1)
        if p != q and phi % e:
            return p * q, e, pow(e, -1, phi)


@pytest.fixture(scope="module")
def key() -> tuple[int, int, int]:
    return make_key(2026)


@pytest.fixture(scope="module")
def other_key() -> tuple[int, int, int]:
    return make_key(1999)


def number(value: int) -> str:
    return jwtlib.b64url(value.to_bytes((value.bit_length() + 7) // 8, "big"))


def jwks(key: tuple[int, int, int], kid: str = "2026") -> dict:
    n, e, _ = key
    return {"keys": [{"kty": "RSA", "kid": kid, "n": number(n), "e": number(e)}]}


def token(
    key: tuple[int, int, int],
    claims: dict | None = None,
    header: dict | None = None,
    drop: tuple[str, ...] = (),
) -> str:
    """A signed token: the usual claims, with `claims` laid over them."""
    n, _, d = key
    payload = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": "ana",
        "iat": NOW - 10,
        "exp": NOW + 290,
        "nonce": "abc123",
    }
    payload.update(claims or {})
    for name in drop:
        del payload[name]
    head = {"alg": "RS256", "typ": "JWT", "kid": "2026"}
    head.update(header or {})
    signed = (
        jwtlib.b64url(json.dumps(head).encode())
        + "."
        + jwtlib.b64url(json.dumps(payload).encode())
    )
    size = (n.bit_length() + 7) // 8
    block = int.from_bytes(jwtlib.rs256_block(signed.encode(), size), "big")
    return signed + "." + jwtlib.b64url(pow(block, d, n).to_bytes(size, "big"))


def verdict(tok: str, keys: dict, **options) -> str:
    options.setdefault("now", NOW)
    return jwtlib.verify(tok, ISSUER, AUDIENCE, keys, **options)[0]


def test_a_good_token_is_valid_and_its_claims_come_back(key) -> None:
    result, payload = jwtlib.verify(
        token(key), ISSUER, AUDIENCE, jwks(key), nonce="abc123", now=NOW
    )
    assert result == "valid"
    assert payload["sub"] == "ana"


def test_an_audience_may_be_one_of_a_list(key) -> None:
    listed = token(key, {"aud": ["account", AUDIENCE]})
    assert verdict(listed, jwks(key)) == "valid"
    assert verdict(token(key, {"aud": ["account"]}), jwks(key)) == "audience"


def test_format(key) -> None:
    good = token(key)
    assert verdict("not a token", jwks(key)) == "format"
    assert verdict(good.rsplit(".", 1)[0], jwks(key)) == "format"
    assert verdict("!!!." + good.split(".", 1)[1], jwks(key)) == "format"
    # A payload that is JSON but not an object.
    head, _, sig = good.split(".")
    assert verdict(f"{head}.{jwtlib.b64url(b'[1]')}.{sig}", jwks(key)) == "format"


def test_alg_is_the_verifiers_choice_never_the_tokens(key) -> None:
    # "none" with an empty signature, and HS256: both stop at alg, before
    # any key is looked at (RFC 8725, section 3.1).
    head, payload, _ = token(key, header={"alg": "none"}).split(".")
    assert verdict(f"{head}.{payload}.", jwks(key)) == "alg"
    assert verdict(token(key, header={"alg": "HS256"}), jwks(key)) == "alg"


def test_key(key) -> None:
    assert verdict(token(key, header={"kid": "2031"}), jwks(key)) == "key"
    assert verdict(token(key), {"keys": []}) == "key"
    # A key of another kind under the right name.
    assert verdict(token(key), {"keys": [{"kty": "EC", "kid": "2026"}]}) == "key"


def test_signature(key, other_key) -> None:
    # Signed by someone else under the issuer's key name.
    assert verdict(token(other_key), jwks(key)) == "signature"
    # One claim changed after signing.
    head, _, sig = token(key).split(".")
    forged = token(key, {"sub": "ben"}).split(".")[1]
    assert verdict(f"{head}.{forged}.{sig}", jwks(key)) == "signature"
    # A signature of the wrong length, and an empty one.
    assert verdict(f"{head}.{forged}.{sig[:-4]}", jwks(key)) == "signature"
    assert verdict(f"{head}.{forged}.", jwks(key)) == "signature"


def test_a_key_under_2048_bits_signs_nothing() -> None:
    small = make_key(7, bits=1024)
    assert verdict(token(small), jwks(small)) == "signature"


def test_issuer(key) -> None:
    other = token(key, {"iss": "https://login.shop-help.test/realms/shop"})
    assert verdict(other, jwks(key)) == "issuer"
    # A trailing slash is another issuer: the comparison is exact.
    assert verdict(token(key, {"iss": ISSUER + "/"}), jwks(key)) == "issuer"


def test_audience(key) -> None:
    assert verdict(token(key, {"aud": "shop-web"}), jwks(key)) == "audience"
    assert verdict(token(key, drop=("aud",)), jwks(key)) == "audience"


def test_expired(key) -> None:
    assert verdict(token(key, {"exp": NOW - 61}), jwks(key)) == "expired"
    # The leeway forgives a minute of clock difference, and no more.
    assert verdict(token(key, {"exp": NOW - 59}), jwks(key)) == "valid"
    assert verdict(token(key, {"exp": NOW - 59}), jwks(key), leeway=0) == "expired"
    # A token with no expiry is refused, not trusted for ever.
    assert verdict(token(key, drop=("exp",)), jwks(key)) == "expired"


def test_not_yet_valid(key) -> None:
    assert verdict(token(key, {"iat": NOW + 61}), jwks(key)) == "not-yet-valid"
    assert verdict(token(key, {"iat": NOW + 59}), jwks(key)) == "valid"
    # nbf, when the token has one, is what counts.
    early = token(key, {"nbf": NOW + 120})
    assert verdict(early, jwks(key)) == "not-yet-valid"


def test_nonce(key) -> None:
    assert verdict(token(key), jwks(key), nonce="other") == "nonce"
    assert verdict(token(key, drop=("nonce",)), jwks(key), nonce="abc123") == "nonce"
    # Nobody asked for a nonce: none is checked.
    assert verdict(token(key, drop=("nonce",)), jwks(key)) == "valid"


def test_the_first_fault_is_the_one_named(key, other_key) -> None:
    # The order a careful verifier checks in: a token wrong in every way is
    # reported for its signature, and once that is right, for its issuer.
    wrong = {"iss": "https://evil.test", "aud": "x", "exp": NOW - 999}
    assert verdict(token(other_key, wrong), jwks(key)) == "signature"
    assert verdict(token(key, wrong), jwks(key)) == "issuer"
    assert verdict(token(key, {"aud": "x", "exp": NOW - 999}), jwks(key)) == "audience"


def test_the_stock_apis_two_switches(key) -> None:
    # audience None and leeway None are what check_audience = no and
    # check_expiry = no pass: the faults a hurried fix switches off.
    for_site = token(key, {"aud": "shop-web"})
    assert jwtlib.verify(for_site, ISSUER, None, jwks(key), now=NOW)[0] == "valid"
    old = token(key, {"exp": NOW - 999})
    assert jwtlib.verify(old, ISSUER, AUDIENCE, jwks(key), None, None, NOW)[0] == (
        "valid"
    )
