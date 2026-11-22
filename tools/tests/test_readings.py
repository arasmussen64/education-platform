"""Readings shown inside the app (ADR-0031): the validator accepts a copy
made as content/README.md says, and catches each kind of mistake."""

from pathlib import Path

import pytest
import reading_html
from content_fixture import TOPIC, make_valid_tree, write
from validate_content import validate

TOPIC_DIR = "content/topics/t.hello"

VIDEO = """  - title: A video
    url: https://www.youtube.com/watch?v=abc
    type: video
    use: embed
    start: 10
    end: 20
    license: CC BY-NC-SA 4.0
"""

GOOD_HTML = "<h3>Print</h3>\n<p>The <code>print</code> function shows text.</p>\n"


def reading(
    license_text: str = "CC BY 4.0", use: str = "embed", text: bool = True
) -> str:
    copy = (
        "    text:\n"
        "      file: readings/print.html\n"
        "      by: the Example Foundation\n"
        "      license_url: https://example.com/license\n"
        '      retrieved: "2026-11-21"\n'
        "      changes: Only the section Print.\n"
    )
    return (
        "  - title: A page\n"
        "    url: https://example.com/page\n"
        "    type: reading\n"
        f"    use: {use}\n"
        f"    license: {license_text}\n" + (copy if text else "")
    )


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    return make_valid_tree(tmp_path)


def with_reading(root: Path, resource: str, html: str | None = GOOD_HTML) -> None:
    assert VIDEO in TOPIC
    write(root, f"{TOPIC_DIR}/topic.yaml", TOPIC.replace(VIDEO, VIDEO + resource))
    if html is not None:
        write(root, f"{TOPIC_DIR}/readings/print.html", html)


def problems(root: Path) -> list[str]:
    return validate(root, run=False).problems


def assert_reported(root: Path, fragment: str) -> None:
    found = problems(root)
    assert any(fragment in problem for problem in found), (
        f"expected a problem mentioning {fragment!r}, got: {found}"
    )


def test_a_good_copy_passes(tree: Path) -> None:
    with_reading(tree, reading())
    assert problems(tree) == []


def test_the_copy_must_exist(tree: Path) -> None:
    with_reading(tree, reading(), html=None)
    assert_reported(tree, "which doesn't exist")


def test_a_copy_nothing_names_is_caught(tree: Path) -> None:
    write(tree, f"{TOPIC_DIR}/readings/stray.html", GOOD_HTML)
    assert_reported(tree, "no resource's text: names this file")


@pytest.mark.parametrize(
    ("license_text", "fragment"),
    [
        ("Copyright Example Corp; linked, not copied", "allows copying"),
        ("CC BY-NC-ND 4.0", "allows copying"),
        ("No licence stated", "allows copying"),
        ("CC BY-SA 4.0 (linked, not copied)", 'still says "not copied"'),
    ],
)
def test_only_a_licence_that_allows_copying_may_carry_a_copy(
    tree: Path, license_text: str, fragment: str
) -> None:
    with_reading(tree, reading(license_text))
    assert_reported(tree, fragment)


def test_embed_needs_a_video_or_a_copy(tree: Path) -> None:
    with_reading(tree, reading(text=False), html=None)
    assert_reported(tree, "use: embed is only for")


def test_a_copy_needs_use_embed(tree: Path) -> None:
    with_reading(tree, reading(use="link"))
    assert_reported(tree, "text: is only for a reading with use: embed")


@pytest.mark.parametrize(
    ("html", "fragment"),
    [
        ("<p>Hi</p><script>steal()</script>", "<script> isn't allowed"),
        ('<p onclick="steal()">Hi</p>', "<p onclick"),
        ('<p style="color: red">Hi</p>', "<p style"),
        ("<div><p>Hi</p></div>", "<div> isn't allowed"),
        ('<p><a href="javascript:steal()">Hi</a></p>', "full https:// address"),
        ('<p><a href="/local">Hi</a></p>', "full https:// address"),
        ('<p>Hi <img src="http://example.com/a.png" alt=""></p>', "full https://"),
        ("<p>Hi</p><!-- a note -->", "comments aren't allowed"),
        ("<p></p>", "the reading is empty"),
    ],
)
def test_a_copy_holds_only_plain_html(tree: Path, html: str, fragment: str) -> None:
    with_reading(tree, reading(), html)
    assert_reported(tree, fragment)


def test_tables_pictures_and_formulas_are_plain_enough() -> None:
    html = (
        '<table><thead><tr><th colspan="2">Rate</th></tr></thead>'
        "<tbody><tr><td>5%</td><td>10%</td></tr></tbody></table>"
        '<figure><img src="https://example.com/a.png" alt="A chart">'
        "<figcaption>A chart</figcaption></figure>"
        '<p><math display="block"><mfrac><mn>1</mn><mi>x</mi></mfrac></math></p>'
    )
    found, words = reading_html.check(html)
    assert found == []
    assert words == 7


@pytest.mark.parametrize(
    ("license_text", "allowed"),
    [
        ("CC BY 4.0", True),
        ("CC BY-SA 4.0", True),
        ("CC BY-NC-SA 4.0", True),
        ("CC BY-NC 3.0", True),
        ("PSF License Version 2", True),
        ("BSD-3-Clause (NumPy documentation)", True),
        ("GPL-2.0", True),
        ("GNU FDL 1.3", True),
        ("US government work (SEC)", True),
        ("Public domain (US government work)", True),
        ("CC BY-NC-ND 3.0", False),
        ("CC BY-ND 4.0", False),
        ("Copyright Amazon Web Services", False),
        ("Standard YouTube licence (official embed)", False),
        ("No licence stated", False),
    ],
)
def test_which_licences_allow_copying(license_text: str, allowed: bool) -> None:
    assert reading_html.copyable(license_text) is allowed
