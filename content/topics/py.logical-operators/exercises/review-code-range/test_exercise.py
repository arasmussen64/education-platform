from checks import run

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_inside():
    """Typing 5 prints In range: True."""
    assert run("5\n") == "In range: True\n"


def test_outside():
    """Typing 0 or 11 prints In range: False."""
    assert run("0\n") == "In range: False\n"
    assert run("11\n") == "In range: False\n"


def test_ends():
    """1 and 10 are both in range."""
    assert run("1\n") == "In range: True\n"
    assert run("10\n") == "In range: True\n"
