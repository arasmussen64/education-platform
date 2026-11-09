from pathlib import Path

from checks import function


def test_three_lines():
    """A file with three lines gives 3."""
    Path("three.txt").write_text("a\nbb\nccc\n", encoding="utf-8")
    got = function("count_lines")("three.txt")
    assert got == 3, f"count_lines returned {got!r} for a three-line file"


def test_empty_file():
    """An empty file gives 0."""
    Path("empty.txt").write_text("", encoding="utf-8")
    got = function("count_lines")("empty.txt")
    assert got == 0, f"count_lines returned {got!r} for an empty file"
