from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

EXPECTED = "Year 1: 12.00%\nYear 2: -15.18%\nYear 3: 24.21%\nYear 4: 10.17%\nAnnualized: 6.78%\n"


def close(a, b):
    return abs(a - b) < 1e-6


def test_the_report():
    """Prints each year's return and the annualized return for the fund."""
    assert run() == EXPECTED


def test_simple_returns():
    """simple_returns([50, 55, 44]) is [0.10, -0.20]: one return for each price after the first."""
    simple_returns = function("simple_returns")
    got = simple_returns([50, 55, 44])
    assert isinstance(got, list) and len(got) == 2
    assert close(got[0], 0.10) and close(got[1], -0.20)


def test_yearly_prices():
    """annualized_return([80, 100], 1) is 0.25, and annualized_return([100, 121, 121], 1) is about 0.10."""
    annualized_return = function("annualized_return")
    assert close(annualized_return([80, 100], 1), 0.25)
    assert close(annualized_return([100, 121, 121], 1), 0.10)


def test_monthly_and_quarterly():
    """Seven monthly prices from 100 to 103 annualize to about 6.09%; nine quarterly prices from 100 to 121, to 10%."""
    annualized_return = function("annualized_return")
    assert close(annualized_return([100, 103.0, 101, 99, 104, 102, 103], 12), 0.0609)
    assert close(annualized_return([100, 104, 99, 107, 110, 112, 108, 115, 121], 4), 0.10)
