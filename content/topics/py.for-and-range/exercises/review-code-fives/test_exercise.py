from checks import run

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_seventeen():
    """Typing 17 prints 5, 10, 15."""
    assert run("17\n") == "5\n10\n15\n"


def test_twenty():
    """Typing 20 prints 5, 10, 15, 20: the number itself counts."""
    assert run("20\n") == "5\n10\n15\n20\n"


def test_small():
    """Typing 4 prints nothing."""
    assert run("4\n") == ""
