from checks import run, run_with

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_two_hundred_seconds():
    """Prints 3 min 20 s."""
    assert run() == "3 min 20 s\n"


def test_any_number_of_seconds():
    """Works for any number of seconds, using total_seconds."""
    assert run_with({"total_seconds": 61}) == "1 min 1 s\n"
