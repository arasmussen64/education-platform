from checks import run, run_with

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_as_written():
    """Prints 5 3."""
    assert run() == "5 3\n"


def test_other_start():
    """With a starting at 2, nothing is taken off: it prints 2 3."""
    assert run_with({"a": 2}) == "2 3\n"
