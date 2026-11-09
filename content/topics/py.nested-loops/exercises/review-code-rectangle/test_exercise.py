from checks import run

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_three_by_two():
    """Typing 3 and 2 prints two rows of three stars."""
    assert run("3\n2\n") == "***\n***\n"


def test_two_by_four():
    """Typing 2 and 4 prints four rows of two stars."""
    assert run("2\n4\n") == "**\n**\n**\n**\n"


def test_one_by_one():
    """Typing 1 and 1 prints a single star."""
    assert run("1\n1\n") == "*\n"
