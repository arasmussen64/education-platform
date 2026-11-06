from checks import run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

STARS = "*" * 11


def test_three_lines():
    """Prints three lines."""
    assert len(run().splitlines()) == 3


def test_top_and_bottom():
    """The first and last lines are 11 stars each."""
    lines = run().splitlines()
    assert lines[:1] == [STARS]
    assert lines[-1:] == [STARS]


def test_middle():
    """The middle line is WELCOME, with a space and a star on each side."""
    assert run().splitlines()[1:2] == ["* WELCOME *"]


def test_exactly():
    """Prints exactly the banner, with nothing extra."""
    assert run() == f"{STARS}\n* WELCOME *\n{STARS}\n"
