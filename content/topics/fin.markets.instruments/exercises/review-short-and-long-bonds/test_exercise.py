from checks import run, run_with

# Hidden tests: the learner sees each docstring and whether it passed.


def test_the_table():
    """Prints the three bonds' prices before and after, and the change: -1.9%, -7.8% and -15.9%."""
    assert run() == (
        "2 years: $1,009.50 to $990.64, -1.9%\n"
        "10 years: $1,041.58 to $960.44, -7.8%\n"
        "30 years: $1,091.96 to $918.56, -15.9%\n"
    )


def test_other_rates():
    """Works for other rates: from 5% to 6%."""
    assert run_with({"old_rate": 0.05, "new_rate": 0.06}) == (
        "2 years: $981.41 to $963.33, -1.8%\n"
        "10 years: $922.78 to $852.80, -7.6%\n"
        "30 years: $846.28 to $724.70, -14.4%\n"
    )
