from checks import run, run_with

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_this_investment():
    """Prints Principal: 1500.00, then Check: 180.00 for 180, 4% and 3 years."""
    assert run() == "Principal: 1500.00\nCheck: 180.00\n"


def test_any_investment():
    """Works for any interest, rate and years: the check gives the interest back."""
    printed = run_with({"interest": 50, "rate": 2, "years": 5})
    assert printed == "Principal: 500.00\nCheck: 50.00\n"
