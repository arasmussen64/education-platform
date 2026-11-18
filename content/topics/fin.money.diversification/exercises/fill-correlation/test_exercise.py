from checks import function, run, run_with


def test_stocks_and_gold():
    """Prints Stocks and gold: -0.94."""
    printed = run()
    assert printed == "Stocks and gold: -0.94\n", f"Your program printed:\n{printed}"


def test_moving_together():
    """A list and one that always moves the same way, twice as far, have a correlation of 1."""
    correlation = function("correlation")
    got = correlation([0.01, 0.05, -0.02, 0.03], [0.03, 0.11, -0.03, 0.07])
    assert abs(got - 1.0) < 1e-9, f"correlation returned {got}; a correlation can't be above 1"


def test_other_returns():
    """Works for any two lists: these two give 0.80."""
    printed = run_with(
        {
            "stocks": [0.01, 0.03, -0.02, 0.04, 0.00],
            "gold": [0.02, 0.01, -0.01, 0.05, -0.02],
        }
    )
    assert printed == "Stocks and gold: 0.80\n", (
        f"With other returns it should print Stocks and gold: 0.80. It printed:\n{printed}"
    )
