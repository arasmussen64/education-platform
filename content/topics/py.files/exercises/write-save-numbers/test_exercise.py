from pathlib import Path

from checks import function


def test_writes_lines():
    """After save_numbers("n.txt", [3, 10, 7]) the file holds 3, 10 and 7 on separate lines."""
    function("save_numbers")("n.txt", [3, 10, 7])
    got = Path("n.txt").read_text(encoding="utf-8")
    assert got == "3\n10\n7\n", f"the file contains {got!r}"


def test_replaces_old_contents():
    """Saving again replaces what was there; an empty list leaves an empty file."""
    save_numbers = function("save_numbers")
    save_numbers("again.txt", [1, 2])
    save_numbers("again.txt", [9])
    assert Path("again.txt").read_text(encoding="utf-8") == "9\n"
    save_numbers("again.txt", [])
    assert Path("again.txt").read_text(encoding="utf-8") == ""
