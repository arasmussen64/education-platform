from checks import function, run, run_with

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

TABLE = (
    "0% in A: 8.00%\n"
    "10% in A: 7.76%\n"
    "20% in A: 7.95%\n"
    "30% in A: 8.52%\n"
    "40% in A: 9.42%\n"
    "50% in A: 10.55%\n"
    "60% in A: 11.86%\n"
    "70% in A: 13.29%\n"
    "80% in A: 14.80%\n"
    "90% in A: 16.38%\n"
    "100% in A: 18.00%\n"
    "Lowest risk: 11% in A, volatility 7.76%\n"
)

OTHER_TABLE = (
    "0% in A: 15.00%\n"
    "10% in A: 12.97%\n"
    "20% in A: 11.53%\n"
    "30% in A: 10.92%\n"
    "40% in A: 11.27%\n"
    "50% in A: 12.50%\n"
    "60% in A: 14.39%\n"
    "70% in A: 16.71%\n"
    "80% in A: 19.31%\n"
    "90% in A: 22.10%\n"
    "100% in A: 25.00%\n"
    "Lowest risk: 31% in A, volatility 10.91%\n"
)


def is_number(x):
    return isinstance(x, (int, float))


def test_the_table():
    """Prints the eleven mixes and the lowest-risk mix for 18%, 8% and a correlation of 0.2."""
    assert run() == TABLE


def test_other_funds():
    """Works for other funds: 25% and 15% with a correlation of -0.3."""
    assert run_with({"vol_a": 0.25, "vol_b": 0.15, "corr": -0.3}) == OTHER_TABLE


def test_portfolio_volatility():
    """portfolio_volatility(0.5, 0.2, 0.2, 0.0) is about 0.1414, and (0.25, 0.3, 0.1, 0.4) about 0.1255."""
    portfolio_volatility = function("portfolio_volatility")
    first = portfolio_volatility(0.5, 0.2, 0.2, 0.0)
    second = portfolio_volatility(0.25, 0.3, 0.1, 0.4)
    assert is_number(first) and abs(first - 0.141421) < 1e-5
    assert is_number(second) and abs(second - 0.125499) < 1e-5


def test_lowest_risk_mix():
    """lowest_risk_mix(0.3, 0.1, 0.0) returns the weight 0.1 and a volatility of about 0.0949."""
    lowest_risk_mix = function("lowest_risk_mix")
    got = lowest_risk_mix(0.3, 0.1, 0.0)
    assert isinstance(got, tuple) and len(got) == 2
    weight, vol = got
    assert is_number(weight) and abs(weight - 0.1) < 1e-9
    assert is_number(vol) and abs(vol - 0.094868) < 1e-5
