from checks import function, run, run_with

EXPECTED = (
    "Value at 8%: $49.56\n"
    "Value at 10%: $45.52\n"
    "Value if the sale price is $50.00: $42.75\n"
)


def test_one_year():
    """share_value([3.0], 50, 0.1) is about 48.18: $53 a year from now, discounted at 10%."""
    share_value = function("share_value")
    got = share_value([3.0], 50, 0.1)
    assert abs(got - 48.1818) < 0.005, f"share_value([3.0], 50, 0.1) returned {got}"


def test_two_years():
    """share_value([1.0, 1.0], 20, 0.1) is about 18.26."""
    share_value = function("share_value")
    got = share_value([1.0, 1.0], 20, 0.1)
    assert abs(got - 18.2645) < 0.005, f"share_value([1.0, 1.0], 20, 0.1) returned {got}"


def test_the_report():
    """Prints the three values."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_another_share():
    """Works for another share: three dividends of $0.50, a sale price of $30, at 7%."""
    expected = (
        "Value at 7%: $25.80\n"
        "Value at 9%: $24.43\n"
        "Value if the sale price is $20.00: $17.64\n"
    )
    printed = run_with({"dividends": [0.5, 0.5, 0.5], "sale_price": 30.0, "rate": 0.07})
    assert printed == expected, f"For that share it should print:\n{expected}\nIt printed:\n{printed}"
