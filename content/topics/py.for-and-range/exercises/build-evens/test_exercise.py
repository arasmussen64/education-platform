from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_seven():
    """Typing 7 prints 2, 4, 6."""
    assert run("7\n") == "2\n4\n6\n"


def test_eight():
    """Typing 8 prints 2, 4, 6, 8: the number itself counts when it's even."""
    assert run("8\n") == "2\n4\n6\n8\n"


def test_small():
    """Typing 1 prints nothing, and typing 2 prints just 2."""
    assert run("1\n") == ""
    assert run("2\n") == "2\n"
