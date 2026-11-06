from checks import run

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_paris():
    """Typing Paris prints Welcome to Paris!"""
    assert run("Paris\n") == "Welcome to Paris!\n"


def test_any_city():
    """Works for any city typed in."""
    assert run("Lima\n") == "Welcome to Lima!\n"
