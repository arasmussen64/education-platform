from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_three_numbers():
    """Typing 4, 9, 2, 0 prints Count: 3, Total: 15, Largest: 9."""
    assert run("4\n9\n2\n0\n") == "Count: 3\nTotal: 15\nLargest: 9\n"


def test_none():
    """Typing 0 straight away prints three zeros."""
    assert run("0\n") == "Count: 0\nTotal: 0\nLargest: 0\n"


def test_largest_first():
    """Typing 5, 1, 2, 0 prints Largest: 5: the largest isn't always the last."""
    assert run("5\n1\n2\n0\n") == "Count: 3\nTotal: 8\nLargest: 5\n"
