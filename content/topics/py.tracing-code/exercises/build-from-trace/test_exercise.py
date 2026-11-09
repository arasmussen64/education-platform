from checks import run, run_with

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_as_written():
    """With score 50 and bonus 20, prints High, then 70 20."""
    assert run() == "High\n70 20\n"


def test_low_score():
    """With score starting at 30, the bonus is lost: Low, then 30 0."""
    assert run_with({"score": 30}) == "Low\n30 0\n"


def test_small_bonus():
    """With score 55 and bonus 2, the score only reaches 57: Low, then 57 2."""
    assert run_with({"score": 55, "bonus": 2}) == "Low\n57 2\n"


def test_exactly_fifty():
    """50 counts as at least 50, so it gets the bonus."""
    assert run_with({"score": 50, "bonus": 11}) == "High\n61 11\n"
