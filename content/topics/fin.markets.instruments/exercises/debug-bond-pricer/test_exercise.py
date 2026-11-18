from checks import run, run_with

EXPECTED = "Price: $929.08\nBelow face value: the market wants more than the coupon pays\n"


def test_the_price():
    """Prints Price: $929.08 and says it's below face value."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_another_bond():
    """Works for another bond: $2,000 paying 6% for 5 years at a market rate of 4% is $2,178.07."""
    expected = "Price: $2,178.07\nAt or above face value: the coupon pays at least what the market wants\n"
    printed = run_with({"face": 2000, "coupon_rate": 0.06, "years": 5, "market_rate": 0.04})
    assert printed == expected, f"For that bond it should print:\n{expected}\nIt printed:\n{printed}"
