"""cors-verdict, the network labs' model of a browser's CORS decision
(content/lab-bases/net/cors-verdict), against a table of cases worked out by
hand from the Fetch standard's "CORS check" and "CORS-preflight fetch"
(https://fetch.spec.whatwg.org/, read 2026-11-12).

The HTTP semantics topic's checks compare a learner's nginx answers, and the
write lab's script, with it, so a wrong verdict here would pass wrong work.
The write lab is a plain lab that can't see the base, so it carries a copy
of the file; the last test fails if the two copies differ.
"""

import importlib.machinery
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BASE_COPY = ROOT / "content" / "lab-bases" / "net" / "cors-verdict"
LAB_COPY = (
    ROOT
    / "content"
    / "topics"
    / "csa.net.http-semantics"
    / "exercises"
    / "write-cors-audit"
    / "cors-verdict"
)


def load():
    loader = importlib.machinery.SourceFileLoader("cors_verdict", str(BASE_COPY))
    spec = importlib.util.spec_from_loader("cors_verdict", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


cors = load()

SHOP = "https://www.shop.test"


def reply(status: int, *headers: str) -> str:
    """An answer as curl -si prints it: status line, headers, blank, body."""
    lines = [f"HTTP/1.1 {status} X", *headers, "", "{}"]
    return "\r\n".join(lines)


ALLOW_ALL = reply(
    204,
    f"Access-Control-Allow-Origin: {SHOP}",
    "Access-Control-Allow-Credentials: true",
    "Access-Control-Allow-Methods: GET, PUT, DELETE",
    "Access-Control-Allow-Headers: Content-Type, X-Request-Id",
)
ACTUAL_OK = reply(
    200,
    f"Access-Control-Allow-Origin: {SHOP}",
    "Access-Control-Allow-Credentials: true",
)
NOTHING = reply(200)
JSON = "Content-Type: application/json"

# (name, preflight answer, actual answer, method, header, credentials, verdict)
CASES = [
    ("exact allow", ALLOW_ALL, ACTUAL_OK, "PUT", JSON, True, "allowed"),
    (
        "names in lower case",
        reply(
            204,
            f"access-control-allow-origin: {SHOP}",
            "access-control-allow-credentials: true",
            "access-control-allow-methods: PUT",
            "access-control-allow-headers: content-type",
        ),
        reply(
            200,
            f"access-control-allow-origin: {SHOP}",
            "access-control-allow-credentials: true",
        ),
        "PUT",
        JSON,
        True,
        "allowed",
    ),
    (
        "no allow-origin on the preflight",
        reply(204, "Access-Control-Allow-Methods: PUT"),
        ACTUAL_OK,
        "PUT",
        "",
        False,
        "blocked: no allow-origin",
    ),
    (
        "another origin",
        reply(204, "Access-Control-Allow-Origin: https://shop.test"),
        ACTUAL_OK,
        "DELETE",
        "",
        False,
        "blocked: origin not allowed",
    ),
    (
        "the origin with a trailing slash",
        reply(
            204,
            f"Access-Control-Allow-Origin: {SHOP}/",
            "Access-Control-Allow-Methods: PUT",
        ),
        ACTUAL_OK,
        "PUT",
        "",
        False,
        "blocked: origin not allowed",
    ),
    (
        "two allow-origin headers",
        reply(
            204,
            f"Access-Control-Allow-Origin: {SHOP}",
            "Access-Control-Allow-Origin: https://shop.test",
            "Access-Control-Allow-Methods: PUT",
        ),
        ACTUAL_OK,
        "PUT",
        "",
        False,
        "blocked: origin not allowed",
    ),
    (
        "a wildcard without credentials",
        reply(
            204,
            "Access-Control-Allow-Origin: *",
            "Access-Control-Allow-Methods: *",
            "Access-Control-Allow-Headers: *",
        ),
        reply(200, "Access-Control-Allow-Origin: *"),
        "PATCH",
        "X-Request-Id: 7",
        False,
        "allowed",
    ),
    (
        "a wildcard with credentials",
        reply(
            204,
            "Access-Control-Allow-Origin: *",
            "Access-Control-Allow-Credentials: true",
            "Access-Control-Allow-Methods: PUT",
            "Access-Control-Allow-Headers: Content-Type",
        ),
        ACTUAL_OK,
        "PUT",
        JSON,
        True,
        "blocked: wildcard with credentials",
    ),
    (
        "credentials without allow-credentials",
        reply(
            204,
            f"Access-Control-Allow-Origin: {SHOP}",
            "Access-Control-Allow-Methods: PUT",
            "Access-Control-Allow-Headers: Content-Type",
        ),
        ACTUAL_OK,
        "PUT",
        JSON,
        True,
        "blocked: credentials not allowed",
    ),
    (
        "allow-credentials is case-sensitive",
        reply(
            204,
            f"Access-Control-Allow-Origin: {SHOP}",
            "Access-Control-Allow-Credentials: True",
            "Access-Control-Allow-Methods: PUT",
        ),
        ACTUAL_OK,
        "PUT",
        "",
        True,
        "blocked: credentials not allowed",
    ),
    (
        "the method missing",
        reply(
            204,
            f"Access-Control-Allow-Origin: {SHOP}",
            "Access-Control-Allow-Credentials: true",
            "Access-Control-Allow-Methods: GET, PUT",
            "Access-Control-Allow-Headers: Content-Type",
        ),
        ACTUAL_OK,
        "DELETE",
        JSON,
        True,
        "blocked: method not allowed",
    ),
    (
        "a methods wildcard with credentials",
        reply(
            204,
            f"Access-Control-Allow-Origin: {SHOP}",
            "Access-Control-Allow-Credentials: true",
            "Access-Control-Allow-Methods: *",
            "Access-Control-Allow-Headers: Content-Type",
        ),
        ACTUAL_OK,
        "PUT",
        JSON,
        True,
        "blocked: method not allowed",
    ),
    (
        "the header missing",
        reply(
            204,
            f"Access-Control-Allow-Origin: {SHOP}",
            "Access-Control-Allow-Credentials: true",
            "Access-Control-Allow-Methods: PUT",
            "Access-Control-Allow-Headers: X-Requested-With",
        ),
        ACTUAL_OK,
        "PUT",
        JSON,
        True,
        "blocked: header not allowed",
    ),
    (
        "a headers wildcard with credentials",
        reply(
            204,
            f"Access-Control-Allow-Origin: {SHOP}",
            "Access-Control-Allow-Credentials: true",
            "Access-Control-Allow-Methods: PUT",
            "Access-Control-Allow-Headers: *",
        ),
        ACTUAL_OK,
        "PUT",
        JSON,
        True,
        "blocked: header not allowed",
    ),
    (
        "a headers wildcard never covers Authorization",
        reply(
            204,
            "Access-Control-Allow-Origin: *",
            "Access-Control-Allow-Methods: GET",
            "Access-Control-Allow-Headers: *",
        ),
        reply(200, "Access-Control-Allow-Origin: *"),
        "GET",
        "Authorization: Bearer x",
        False,
        "blocked: header not allowed",
    ),
    (
        "a preflight answered 405",
        reply(
            405,
            f"Access-Control-Allow-Origin: {SHOP}",
            "Access-Control-Allow-Credentials: true",
        ),
        ACTUAL_OK,
        "PUT",
        JSON,
        True,
        "blocked: preflight not ok",
    ),
    (
        "a simple GET is never preflighted",
        NOTHING,
        ACTUAL_OK,
        "GET",
        "",
        True,
        "allowed",
    ),
    (
        "a form POST is simple",
        NOTHING,
        reply(200, f"Access-Control-Allow-Origin: {SHOP}"),
        "POST",
        "Content-Type: application/x-www-form-urlencoded",
        False,
        "allowed",
    ),
    (
        "text/plain with a charset is still simple",
        NOTHING,
        reply(200, "Access-Control-Allow-Origin: *"),
        "POST",
        "Content-Type: text/plain; charset=utf-8",
        False,
        "allowed",
    ),
    (
        "an Accept header is simple",
        NOTHING,
        reply(200, "Access-Control-Allow-Origin: *"),
        "HEAD",
        "Accept: application/json",
        False,
        "allowed",
    ),
    (
        "one byte range is simple",
        NOTHING,
        reply(206, "Access-Control-Allow-Origin: *"),
        "GET",
        "Range: bytes=0-99",
        False,
        "allowed",
    ),
    (
        "a header of the page's own is preflighted",
        NOTHING,
        reply(200, "Access-Control-Allow-Origin: *"),
        "GET",
        "X-Request-Id: 7",
        False,
        "blocked: no allow-origin",
    ),
    (
        "a JSON POST is preflighted",
        NOTHING,
        reply(200, f"Access-Control-Allow-Origin: {SHOP}"),
        "POST",
        JSON,
        False,
        "blocked: no allow-origin",
    ),
    (
        "the preflight passes and the answer doesn't",
        ALLOW_ALL,
        reply(200, "Access-Control-Allow-Credentials: true"),
        "PUT",
        JSON,
        True,
        "blocked: no allow-origin",
    ),
    (
        "a simple GET whose answer allows another origin",
        NOTHING,
        reply(200, "Access-Control-Allow-Origin: https://evil.test"),
        "GET",
        "",
        False,
        "blocked: origin not allowed",
    ),
    (
        "a 100 Continue before the answer",
        "HTTP/1.1 100 Continue\r\n\r\n" + ALLOW_ALL,
        "HTTP/1.1 100 Continue\r\n\r\n" + ACTUAL_OK,
        "PUT",
        JSON,
        True,
        "allowed",
    ),
]


@pytest.mark.parametrize(
    "preflight, actual, method, header, credentials, expected",
    [case[1:] for case in CASES],
    ids=[case[0] for case in CASES],
)
def test_verdict(tmp_path, preflight, actual, method, header, credentials, expected):
    (tmp_path / "pre").write_bytes(preflight.encode())
    (tmp_path / "act").write_bytes(actual.encode())
    pre = cors.answer(tmp_path / "pre")
    act = cors.answer(tmp_path / "act")
    reason = cors.verdict(pre, act, SHOP, method, header, credentials)
    assert (f"blocked: {reason}" if reason else "allowed") == expected


def test_main_prints_the_verdict(tmp_path, capsys):
    (tmp_path / "pre").write_bytes(ALLOW_ALL.encode())
    (tmp_path / "act").write_bytes(ACTUAL_OK.encode())
    cors.main(
        [
            str(tmp_path / "pre"),
            str(tmp_path / "act"),
            SHOP,
            "PUT",
            JSON,
            "--credentials",
        ]
    )
    assert capsys.readouterr().out == "allowed\n"


def test_the_write_labs_copy_is_the_same():
    assert LAB_COPY.exists(), f"{LAB_COPY} is missing"
    base = BASE_COPY.read_bytes().replace(b"\r\n", b"\n")
    lab = LAB_COPY.read_bytes().replace(b"\r\n", b"\n")
    assert lab == base, (
        "The write lab's cors-verdict differs from the base's: copy "
        "content/lab-bases/net/cors-verdict over it, so both decide alike."
    )
