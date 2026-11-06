from checks import run, run_with

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_party():
    """Prints slices each, left over and cost each for 23 slices, 4 people, 30."""
    assert run() == "Slices each: 5\nLeft over: 3\nCost each: 7.5\n"


def test_any_party():
    """Works for any party, using slices, people and cost."""
    printed = run_with({"slices": 10, "people": 3, "cost": 12})
    assert printed == "Slices each: 3\nLeft over: 1\nCost each: 4.0\n"
