from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_three():
    """Typing 3 prints three rows, right-aligned: two spaces and a #, then one space and ##, then ###."""
    assert run("3\n") == "  #\n ##\n###\n"


def test_one():
    """Typing 1 prints a single # with no spaces."""
    assert run("1\n") == "#\n"


def test_four():
    """Typing 4 prints four rows, each four characters wide."""
    assert run("4\n") == "   #\n  ##\n ###\n####\n"
