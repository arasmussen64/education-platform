from checks import run

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_same():
    """Typing cat and cat prints Same word: True."""
    assert run("cat\ncat\n") == "Same word: True\n"


def test_different():
    """Typing cat and dog prints Same word: False."""
    assert run("cat\ndog\n") == "Same word: False\n"


def test_other_words():
    """Works for any pair of words."""
    assert run("tea\ntea\n") == "Same word: True\n"
    assert run("Tea\ntea\n") == "Same word: False\n"
