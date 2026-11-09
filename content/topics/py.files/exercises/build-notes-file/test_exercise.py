from pathlib import Path

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_save_lines():
    """save_lines writes one line each and replaces old contents."""
    save_lines = function("save_lines")
    save_lines("s.txt", ["a", "b"])
    assert Path("s.txt").read_text(encoding="utf-8") == "a\nb\n"
    save_lines("s.txt", ["only"])
    assert Path("s.txt").read_text(encoding="utf-8") == "only\n"


def test_append_line():
    """append_line adds to the end and keeps what was there."""
    Path("ap.txt").write_text("one\n", encoding="utf-8")
    function("append_line")("ap.txt", "two")
    assert Path("ap.txt").read_text(encoding="utf-8") == "one\ntwo\n"


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
