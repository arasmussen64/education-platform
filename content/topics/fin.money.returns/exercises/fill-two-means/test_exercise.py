from checks import run, run_with


def test_three_years():
    """Prints an arithmetic mean of 6.67% and a geometric mean of 4.59%."""
    printed = run()
    expected = "Arithmetic mean: 6.67%\nGeometric mean: 4.59%\n"
    assert printed == expected, f"Expected this:\n{expected}\nYour program printed:\n{printed}"


def test_any_returns():
    """Works for any returns: +15%, −5%, +10%, −8% give 3.00% and 2.54%."""
    printed = run_with({"returns": [0.15, -0.05, 0.10, -0.08]})
    expected = "Arithmetic mean: 3.00%\nGeometric mean: 2.54%\n"
    assert printed == expected, (
        f"With returns = [0.15, -0.05, 0.10, -0.08] it should print:\n{expected}\nIt printed:\n{printed}"
    )
