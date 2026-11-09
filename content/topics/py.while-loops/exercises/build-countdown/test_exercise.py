from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_from_three():
    """Typing 3 prints 3, 2, 1, then Go!"""
    assert run("3\n") == "3\n2\n1\nGo!\n"


def test_from_one():
    """Typing 1 prints 1, then Go!"""
    assert run("1\n") == "1\nGo!\n"


def test_from_five():
    """Typing 5 prints 5 down to 1, then Go!"""
    assert run("5\n") == "5\n4\n3\n2\n1\nGo!\n"
