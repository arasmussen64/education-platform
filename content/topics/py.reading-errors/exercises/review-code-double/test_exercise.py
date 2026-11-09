from checks import run

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_four():
    """Typing 4 prints 8."""
    assert run("4\n") == "8\n"


def test_other_numbers():
    """Typing 7 prints 14, and typing 0 prints 0."""
    assert run("7\n") == "14\n"
    assert run("0\n") == "0\n"
