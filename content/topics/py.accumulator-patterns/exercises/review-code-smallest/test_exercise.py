from checks import run

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_three():
    """Typing 3, 8, 2, 0 prints 2."""
    assert run("3\n8\n2\n0\n") == "2\n"


def test_one():
    """Typing 6, 0 prints 6."""
    assert run("6\n0\n") == "6\n"


def test_smallest_first():
    """Typing 5, 5, 9, 0 prints 5: the smallest isn't always the last."""
    assert run("5\n5\n9\n0\n") == "5\n"
