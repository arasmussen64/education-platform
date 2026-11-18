from checks import function, run, run_with

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def is_number(x):
    return isinstance(x, (int, float))


def test_the_table():
    """Prints the 4% six-year bond's price at market rates of 2%, 4% and 6%."""
    assert run() == "At 2%: $1,112.03\nAt 4%: $1,000.00\nAt 6%: $901.65\n"


def test_another_bond():
    """Works for another bond: $500 paying 5% for 10 years."""
    printed = run_with({"face": 500, "coupon_rate": 0.05, "years": 10})
    assert printed == "At 2%: $634.74\nAt 4%: $540.55\nAt 6%: $463.20\n"


def test_one_year_at_par():
    """bond_price(100, 0.1, 1, 0.1) is 100: a bond whose coupon matches the market is worth its face value."""
    bond_price = function("bond_price")
    got = bond_price(100, 0.1, 1, 0.1)
    assert is_number(got) and abs(got - 100) < 0.005


def test_rates_up_price_down():
    """bond_price(1000, 0.05, 3, 0.07) is about 947.51, and with no coupon over 10 years at 5% about 613.91."""
    bond_price = function("bond_price")
    first = bond_price(1000, 0.05, 3, 0.07)
    second = bond_price(1000, 0, 10, 0.05)
    assert is_number(first) and abs(first - 947.51) < 0.005
    assert is_number(second) and abs(second - 613.91) < 0.005
