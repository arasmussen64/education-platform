from checks import function, run


def test_the_two_lines():
    """Prints the six months' total, 4.49%, and the annualized return, 9.19%."""
    printed = run()
    expected = "Six months: 4.49%\nAnnualized: 9.19%\n"
    assert printed == expected, f"Expected this:\n{expected}\nYour program printed:\n{printed}"


def test_a_full_year():
    """Twelve months of 1% annualize to about 12.68%."""
    annualize_monthly = function("annualize_monthly")
    got = annualize_monthly([0.01] * 12)
    assert abs(got - 0.126825) < 1e-5, f"annualize_monthly([0.01] * 12) returned {got}; expected about 0.1268."


def test_other_lengths():
    """Three months of −1% annualize to about −11.36%, and one month of +5% to about 79.59%."""
    annualize_monthly = function("annualize_monthly")
    got = annualize_monthly([-0.01, -0.01, -0.01])
    assert abs(got - (-0.113615)) < 1e-5, f"annualize_monthly([-0.01, -0.01, -0.01]) returned {got}; expected about -0.1136."
    got = annualize_monthly([0.05])
    assert abs(got - 0.795856) < 1e-5, f"annualize_monthly([0.05]) returned {got}; expected about 0.7959."
