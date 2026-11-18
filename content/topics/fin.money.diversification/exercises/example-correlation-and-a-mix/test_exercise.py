from checks import run


def test_the_report():
    """Prints the correlation, both volatilities, and the mix's volatility both ways."""
    assert run() == (
        "Correlation: 0.22\n"
        "Fund A: 3.41%, fund B: 1.86%\n"
        "Half and half, by the formula: 2.11%\n"
        "Half and half, month by month: 2.11%\n"
    )
