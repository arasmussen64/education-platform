from checks import run

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_from_two():
    """Typing 2 prints 2, 1, 0."""
    assert run("2\n") == "2\n1\n0\n"


def test_from_zero():
    """Typing 0 prints just 0."""
    assert run("0\n") == "0\n"


def test_from_four():
    """Typing 4 prints 4 down to 0."""
    assert run("4\n") == "4\n3\n2\n1\n0\n"
