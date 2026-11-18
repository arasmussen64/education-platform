from checks import run, run_with


def test_the_two_returns():
    """Prints the price-weighted return, +0.4%, and the cap-weighted return, +16.7%."""
    printed = run()
    expected = "price-weighted: +0.4%\ncap-weighted: +16.7%\n"
    assert printed == expected, f"Expected this:\n{expected}\nYour program printed:\n{printed}"


def test_other_companies():
    """Works for other companies: P (100 shares, 10 to 12) and Q (4 shares, 250 to 210) give -14.6% and +2.0%."""
    printed = run_with({"companies": {"P": {"shares": 100, "start": 10.0, "end": 12.0}, "Q": {"shares": 4, "start": 250.0, "end": 210.0}}})
    expected = "price-weighted: -14.6%\ncap-weighted: +2.0%\n"
    assert printed == expected, f"With P and Q it should print:\n{expected}\nIt printed:\n{printed}"
