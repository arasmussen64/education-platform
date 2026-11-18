from checks import function, run, run_with

TABLE = "300 a month: 37 months\n350 a month: 31 months\n400 a month: 27 months\n"


def test_the_function():
    """months_to_repay(1000, 0.02, 100) is 12 months."""
    months_to_repay = function("months_to_repay")
    assert months_to_repay(1000, 0.02, 100) == 12, (
        f"months_to_repay(1000, 0.02, 100) returned {months_to_repay(1000, 0.02, 100)}"
    )


def test_the_table():
    """Prints 37, 31 and 27 months for $300, $350 and $400 a month."""
    printed = run()
    assert printed == TABLE, f"Expected this:\n{TABLE}\nYour program printed:\n{printed}"


def test_another_loan():
    """Works for another loan: 5,000 at 12% a year takes 29 months at 200 and 23 at 250."""
    expected = "200 a month: 29 months\n250 a month: 23 months\n"
    printed = run_with({"principal": 5000, "yearly_rate": 0.12, "payments": [200, 250]})
    assert printed == expected, (
        f"With principal = 5000, yearly_rate = 0.12 and payments = [200, 250] it should "
        f"print:\n{expected}\nIt printed:\n{printed}"
    )
