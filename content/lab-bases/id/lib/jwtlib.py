"""Reading and checking JSON Web Tokens, for "jwt", the stock API and the
checks. RS256 only, by design: the verifier chooses the algorithm, never
the token (RFC 8725).

Standard library only, so the tests in tools/tests/test_idlab_jwtlib.py run
anywhere. An RS256 signature is checked the long way round, with no
parsing of anything an attacker wrote: build the one block a correct
signature of these bytes must decrypt to (RFC 8017, section 9.2), raise the
signature to the public exponent, and compare the two whole."""

import base64
import hashlib
import json
import time
import urllib.request

# The fixed bytes that say "what follows is a SHA-256 hash" (RFC 8017,
# section 9.2, note 1).
SHA256_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")


def b64url_decode(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def parts(token):
    """(header, payload, signed bytes, signature) or raises ValueError."""
    pieces = token.strip().split(".")
    if len(pieces) != 3:
        raise ValueError("format")
    try:
        header = json.loads(b64url_decode(pieces[0]))
        payload = json.loads(b64url_decode(pieces[1]))
        signature = b64url_decode(pieces[2])
    except Exception as error:
        raise ValueError("format") from error
    if not isinstance(header, dict) or not isinstance(payload, dict):
        raise ValueError("format")
    return header, payload, (pieces[0] + "." + pieces[1]).encode(), signature


def fetch_jwks(url):
    with urllib.request.urlopen(url, timeout=10) as answer:
        return json.load(answer)


def public_numbers(jwk):
    """(n, e) of an RSA key as a JWKS publishes it."""
    n = int.from_bytes(b64url_decode(jwk["n"]), "big")
    e = int.from_bytes(b64url_decode(jwk["e"]), "big")
    return n, e


def rs256_block(signed, size):
    """The block of `size` bytes that an RS256 signature of `signed` holds:
    00 01, then FF bytes, then 00, the SHA-256 marker and the hash."""
    tail = SHA256_PREFIX + hashlib.sha256(signed).digest()
    return b"\x00\x01" + b"\xff" * (size - len(tail) - 3) + b"\x00" + tail


def rs256_ok(signed, signature, n, e):
    """Whether `signature` is the RS256 signature of `signed` by the key
    whose public half is (n, e)."""
    size = (n.bit_length() + 7) // 8
    if len(signature) != size or size < 256:  # 2048 bits at least
        return False
    number = int.from_bytes(signature, "big")
    if number >= n:
        return False
    return pow(number, e, n).to_bytes(size, "big") == rs256_block(signed, size)


def verify(token, issuer, audience, jwks, nonce=None, leeway=60, now=None):
    """ "valid", or the first reason the token fails, in the order a careful
    verifier checks: format, alg, key, signature, issuer, audience, expired,
    not-yet-valid, nonce. jwks is the parsed key set (a dict). audience None
    skips the audience and leeway None the times, for the stock API's two
    switches; a check never passes either."""
    now = time.time() if now is None else now
    try:
        header, payload, signed, signature = parts(token)
    except ValueError:
        return "format", {}
    if header.get("alg") != "RS256":
        return "alg", payload
    keys = [
        k
        for k in jwks.get("keys", [])
        if k.get("kid") == header.get("kid") and k.get("kty") == "RSA"
    ]
    if not keys:
        return "key", payload
    try:
        n, e = public_numbers(keys[0])
    except Exception:  # noqa: BLE001
        return "key", payload
    if not rs256_ok(signed, signature, n, e):
        return "signature", payload
    if payload.get("iss") != issuer:
        return "issuer", payload
    aud = payload.get("aud")
    if (
        audience is not None
        and audience != aud
        and not (isinstance(aud, list) and audience in aud)
    ):
        return "audience", payload
    if leeway is not None:
        expires = payload.get("exp")
        if not isinstance(expires, (int, float)) or now > expires + leeway:
            return "expired", payload
        start = payload.get("nbf", payload.get("iat"))
        if isinstance(start, (int, float)) and now < start - leeway:
            return "not-yet-valid", payload
    if nonce is not None and payload.get("nonce") != nonce:
        return "nonce", payload
    return "valid", payload
