from checks import function, run, run_with

EXPECTED = "Stocks and bonds: -0.46\nStocks with themselves: 1.00\n"


def test_the_report():
    """Prints Stocks and bonds: -0.46 and Stocks with themselves: 1.00."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_volatility():
    """volatility([0.01, 0.03, 0.05]) is 0.02."""
    volatility = function("volatility")
    got = volatility([0.01, 0.03, 0.05])
    assert abs(got - 0.02) < 1e-9, f"volatility([0.01, 0.03, 0.05]) returned {got}"


def test_other_returns():
    """Works for any two lists: these two give 0.82."""
    printed = run_with(
        {
            "stocks": [0.02, -0.01, 0.04, 0.01, -0.03],
            "bonds": [0.01, 0.00, 0.03, -0.01, -0.01],
        }
    )
    assert printed.startswith("Stocks and bonds: 0.82\n"), (
        f"With other returns the first line should be Stocks and bonds: 0.82. It printed:\n{printed}"
    )
