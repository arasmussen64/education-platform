from pathlib import Path

from checks import function

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_longest():
    """The longest line comes back without its line break."""
    Path("lines.txt").write_text("hi\nhello there\nhey\n", encoding="utf-8")
    assert function("longest_line")("lines.txt") == "hello there"


def test_tie_and_empty():
    """The first of two equal lines wins, and an empty file gives an empty string."""
    Path("tie.txt").write_text("abc\nxyz\n", encoding="utf-8")
    Path("none.txt").write_text("", encoding="utf-8")
    longest_line = function("longest_line")
    assert longest_line("tie.txt") == "abc"
    assert longest_line("none.txt") == ""
