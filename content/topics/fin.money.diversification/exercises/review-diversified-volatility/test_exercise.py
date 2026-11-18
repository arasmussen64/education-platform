from checks import function, run, run_with

# Hidden tests: the learner sees each docstring and whether it passed.


def test_the_table():
    """Prints six lines, from n = 1: 25.00% down to n = 1000: 10.03%."""
    assert run() == (
        "n = 1: 25.00%\n"
        "n = 2: 19.04%\n"
        "n = 5: 14.32%\n"
        "n = 10: 12.35%\n"
        "n = 100: 10.26%\n"
        "n = 1000: 10.03%\n"
    )


def test_other_values():
    """Works for other holdings: 20% each with a correlation of 0.5 levels off near 14.14%."""
    assert run_with({"vol": 0.2, "corr": 0.5}) == (
        "n = 1: 20.00%\n"
        "n = 2: 17.32%\n"
        "n = 5: 15.49%\n"
        "n = 10: 14.83%\n"
        "n = 100: 14.21%\n"
        "n = 1000: 14.15%\n"
    )


def test_the_function():
    """diversified_volatility(0.3, 0.0, 9) is 0.1: with no shared part, risk falls as one over the square root of n."""
    diversified_volatility = function("diversified_volatility")
    got = diversified_volatility(0.3, 0.0, 9)
    assert isinstance(got, (int, float)) and abs(got - 0.1) < 1e-9
