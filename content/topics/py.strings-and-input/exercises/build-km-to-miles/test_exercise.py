from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_five():
    """Typing 5 prints That's 3.11 miles."""
    assert run("5\n") == "That's 3.11 miles.\n"


def test_a_marathon():
    """Works with decimals: 42.195 km is 26.22 miles."""
    assert run("42.195\n") == "That's 26.22 miles.\n"


def test_half_a_kilometre():
    """Works for small distances: 0.5 km is 0.31 miles."""
    assert run("0.5\n") == "That's 0.31 miles.\n"
