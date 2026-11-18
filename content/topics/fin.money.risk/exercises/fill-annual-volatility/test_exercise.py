from checks import function, run, run_with


def test_six_months():
    """Prints a monthly volatility of 2.61% and an annual volatility of 9.03%."""
    printed = run()
    expected = "Monthly volatility: 2.61%\nAnnual volatility: 9.03%\n"
    assert printed == expected, f"Expected this:\n{expected}\nYour program printed:\n{printed}"


def test_any_returns():
    """Works for any returns: 0.05, -0.05, 0.05, -0.05 give 5.77% a month and 20.00% a year."""
    printed = run_with({"returns": [0.05, -0.05, 0.05, -0.05]})
    expected = "Monthly volatility: 5.77%\nAnnual volatility: 20.00%\n"
    assert printed == expected, (
        f"With returns = [0.05, -0.05, 0.05, -0.05] it should print:\n{expected}\nIt printed:\n{printed}"
    )


def test_the_function():
    """volatility([0.10, -0.10, 0.0]) is 0.10, the sample standard deviation."""
    volatility = function("volatility")
    got = volatility([0.10, -0.10, 0.0])
    assert abs(got - 0.10) < 1e-9, f"volatility([0.10, -0.10, 0.0]) returned {got}; expected 0.10."
