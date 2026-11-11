from pathlib import Path

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def lines_of(path):
    """The file's lines, without their line breaks.

    Files are compared line by line, not character by character. A file
    whose last line has no line break after it holds the same notes, so on
    its own that isn't a mistake, and a hidden test shouldn't fail for it.
    """
    return Path(path).read_text(encoding="utf-8").splitlines()


def test_save_lines():
    """save_lines writes one line each and replaces old contents."""
    save_lines = function("save_lines")
    save_lines("s.txt", ["a", "b"])
    assert lines_of("s.txt") == ["a", "b"]
    save_lines("s.txt", ["only"])
    assert lines_of("s.txt") == ["only"]


def test_append_line():
    """append_line adds each new line to the end, on a line of its own, and keeps what was there."""
    # Two appends, not one: a missing line break after the first new line
    # only shows when the second one lands on the same line ("twothree").
    Path("ap.txt").write_text("one\n", encoding="utf-8")
    append_line = function("append_line")
    append_line("ap.txt", "two")
    append_line("ap.txt", "three")
    assert lines_of("ap.txt") == ["one", "two", "three"]


def test_load_lines():
    """load_lines gives the lines without line breaks, and [] for a missing file."""
    Path("ld.txt").write_text("x\ny\n", encoding="utf-8")
    load_lines = function("load_lines")
    assert load_lines("ld.txt") == ["x", "y"]
    assert load_lines("no-such-file.txt") == []


def test_count_lines():
    """count_lines counts the lines, and gives 0 for a missing file."""
    Path("ct.txt").write_text("p\nq\nr\n", encoding="utf-8")
    count_lines = function("count_lines")
    assert count_lines("ct.txt") == 3
    assert count_lines("also-missing.txt") == 0


def test_program():
    """Running the program prints 3, then milk, eggs and tea."""
    assert run() == "3\nmilk\neggs\ntea\n"
