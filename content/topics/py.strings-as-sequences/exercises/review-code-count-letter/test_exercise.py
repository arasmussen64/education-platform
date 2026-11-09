from checks import run

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_banana():
    """Typing banana and a prints 3."""
    assert run("banana\na\n") == "3\n"


def test_none():
    """Typing banana and z prints 0."""
    assert run("banana\nz\n") == "0\n"


def test_other_word():
    """Typing letter and t prints 2."""
    assert run("letter\nt\n") == "2\n"
