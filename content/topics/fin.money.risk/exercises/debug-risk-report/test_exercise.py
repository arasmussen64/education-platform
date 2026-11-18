from checks import run, run_with

EXPECTED = "Monthly volatility: 6.80%\nAnnual volatility: 23.56%\nMaximum drawdown: 22.32%\n"


def test_volatility():
    """Prints a monthly volatility of 6.80% and an annual volatility of 23.56%."""
    got = run().splitlines()[:2]
    want = EXPECTED.splitlines()[:2]
    assert got == want, "Expected:\n" + "\n".join(want) + "\nYour program printed:\n" + "\n".join(got)


def test_drawdown():
    """Prints a maximum drawdown of 22.32%, the fall from 112 to 87."""
    got = run().splitlines()[2:]
    want = EXPECTED.splitlines()[2:]
    assert got == want, "Expected:\n" + "\n".join(want) + "\nYour program printed:\n" + "\n".join(got)


def test_other_prices():
    """Works for other prices: a year from 80 to 110 with a fall from 95 to 76 gives 9.78%, 33.89% and 20.00%."""
    printed = run_with({"prices": [80, 84, 79, 90, 95, 86, 76, 82, 99, 104, 97, 101, 110]})
    expected = "Monthly volatility: 9.78%\nAnnual volatility: 33.89%\nMaximum drawdown: 20.00%\n"
    assert printed == expected, f"With other prices it should print:\n{expected}\nIt printed:\n{printed}"
