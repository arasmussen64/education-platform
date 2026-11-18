import re

from checks import function, run, run_with

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7). Each test checks one part, so a
# failure points at one skill (ADR-0012). Value tests read the numbers
# whatever their format and check them against the program's own earlier
# lines; one test checks the format and one the layout.

NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


def numbers(line):
    return [float(found.replace(",", "")) for found in NUMBER.findall(line)]


def lines_starting(printed, start):
    return [line for line in printed.splitlines() if line.startswith(start)]


def close(a, b, within=0.005):
    return abs(a - b) <= within


def schedule_is_consistent(printed, principal, annual_rate, months):
    """Every month's numbers follow from the month before, and the loan is paid off."""
    rows = [numbers(line) for line in lines_starting(printed, "month ")]
    paid = [numbers(line) for line in lines_starting(printed, "payment ")]
    if len(rows) != months or len(paid) != 1 or any(len(row) != 4 for row in rows):
        return False
    each = paid[0][0]
    balance = principal
    for number, interest, repaid, new_balance in rows:
        if not close(interest, balance * annual_rate / 12, 0.006):
            return False
        if not close(interest + repaid, each, 0.011):
            return False
        if not close(new_balance, balance - repaid, 0.011):
            return False
        balance = new_balance
    return close(balance, 0, 0.01)


def test_payment():
    """payment(principal, rate, periods) gives the level payment for a rate per period."""
    payment = function("payment")
    assert close(payment(15000, 0.006, 18), 881.64)
    assert close(payment(9000, 0.05 / 12, 12), 770.47)
    assert close(payment(24000, 0.02, 8), 3276.24)


def test_the_schedule():
    """Each month's interest, principal and balance follow from the month before, ending at zero."""
    assert schedule_is_consistent(run(), 18000, 0.048, 24)


def test_the_totals():
    """The payment is right, and the totals paid and of interest match it to the cent."""
    printed = run()
    paid = lines_starting(printed, "payment ")
    total = lines_starting(printed, "total paid ")
    interest = lines_starting(printed, "total interest ")
    assert len(paid) == 1 and len(total) == 1 and len(interest) == 1
    assert numbers(paid[0]) == [788.07]
    assert numbers(total[0]) == [18913.77]
    assert numbers(interest[0]) == [913.77]


def test_money_format():
    """Every amount of money is printed with two decimal places and commas between thousands."""
    printed = run()
    money_lines = [line for line in printed.splitlines() if line.startswith(("month ", "payment ", "total "))]
    assert len(money_lines) == 27
    for line in money_lines:
        amounts = re.findall(r"(?:interest|principal|balance|payment|paid) (-?[\d,]+\.?\d*)", line)
        assert amounts
        for amount in amounts:
            assert re.fullmatch(r"-?\d{1,3}(?:,\d{3})*\.\d\d", amount)


def test_layout():
    """The report's words and order match the example, with every number replaced."""
    printed = run()
    shape = [NUMBER.sub("N", line) for line in printed.splitlines()]
    expected = (
        ["month N: interest N, principal N, balance N"] * 24
        + ["payment N", "total paid N", "total interest N", "annualized return N%", "volatility N%", "max drawdown N%"]
    )
    assert shape == expected


def test_simple_returns():
    """simple_returns gives each price over the one before, minus 1."""
    simple_returns = function("simple_returns")
    got = simple_returns([50.0, 55.0, 44.0])
    assert len(got) == 2 and close(got[0], 0.1, 1e-9) and close(got[1], -0.2, 1e-9)


def test_annualized_return():
    """annualized_return turns growth over any number of periods into a yearly rate."""
    annualized_return = function("annualized_return")
    assert close(annualized_return([50.0, 52.0, 49.0, 55.0, 51.0, 47.0, 53.0, 58.0, 56.0, 60.0, 59.0, 63.0, 62.0], 12), 0.24, 1e-9)
    assert close(annualized_return([100.0, 110.0, 121.0], 1), 0.1, 1e-9)
    assert close(annualized_return([100.0, 103.0, 104.0, 106.0, 102.0, 109.0, 112.36], 12), 0.262, 0.001)


def test_volatility():
    """volatility is the sample standard deviation of the returns (divided by n - 1)."""
    volatility = function("volatility")
    assert close(volatility([0.1, -0.1, 0.05, -0.05]), 0.0912870929, 1e-8)
    assert close(volatility([0.02, 0.04]), 0.0141421356, 1e-8)


def test_max_drawdown():
    """max_drawdown is the largest fall from a running peak, as a decimal."""
    max_drawdown = function("max_drawdown")
    assert close(max_drawdown([100.0, 120.0, 90.0, 130.0, 104.0, 125.0]), 0.25, 1e-9)
    assert close(max_drawdown([10.0, 11.0, 12.0]), 0.0, 1e-9)
    assert close(max_drawdown([80.0, 60.0, 70.0, 50.0, 90.0]), 0.375, 1e-9)


def test_the_portfolio_report():
    """Prints the price list's annualized return, annualized volatility and maximum drawdown."""
    printed = run()
    found = [lines_starting(printed, start) for start in ("annualized return ", "volatility ", "max drawdown ")]
    assert all(len(lines) == 1 for lines in found)
    assert [numbers(lines[0]) for lines in found] == [[17.5], [16.8], [11.4]]


def test_another_loan_and_prices():
    """Works for another loan and another price list too."""
    printed = run_with(
        {
            "principal": 6000,
            "annual_rate": 0.09,
            "months": 6,
            "prices": [50.0, 52.0, 49.0, 55.0, 51.0, 47.0, 53.0, 58.0, 56.0, 60.0, 59.0, 63.0, 62.0],
        }
    )
    assert schedule_is_consistent(printed, 6000, 0.09, 6)
    portfolio = [numbers(line) for line in printed.splitlines()[-3:]]
    assert portfolio == [[24.0], [26.2], [14.5]]
