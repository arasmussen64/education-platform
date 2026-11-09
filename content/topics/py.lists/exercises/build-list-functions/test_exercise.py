from pathlib import Path

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_total():
    """total([4, 9, 2]) is 15, total([]) is 0, and total([1.5, 1.5]) is 3.0."""
    total = function("total")
    assert total([4, 9, 2]) == 15
    assert total([]) == 0
    assert total([1.5, 1.5]) == 3.0


def test_largest():
    """largest([4, 9, 2]) is 9, and largest([-5, -2, -9]) is -2."""
    largest = function("largest")
    assert largest([4, 9, 2]) == 9
    assert largest([-5, -2, -9]) == -2
    assert largest([7]) == 7


def test_last_item():
    """last_item([4, 9, 2]) is 2, and last_item(["only"]) is "only"."""
    last_item = function("last_item")
    assert last_item([4, 9, 2]) == 2
    assert last_item(["only"]) == "only"


def test_loops_not_builtins():
    """The functions use loops: the file doesn't call sum, max or min."""
    source = Path("solution.py").read_text(encoding="utf-8")
    assert "sum(" not in source and "max(" not in source and "min(" not in source


def test_program():
    """Running the program prints the three lines for [4, 9, 2]."""
    assert run() == "Total: 15\nLargest: 9\nLast: 2\n"
