from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_three_names():
    """Typing Ada King Lovelace prints AKL."""
    assert run("Ada King Lovelace\n") == "AKL\n"


def test_two_names():
    """Typing Grace Hopper prints GH."""
    assert run("Grace Hopper\n") == "GH\n"


def test_one_name():
    """Typing Guido prints G."""
    assert run("Guido\n") == "G\n"
