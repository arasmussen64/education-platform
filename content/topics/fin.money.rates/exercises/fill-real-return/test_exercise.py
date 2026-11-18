from checks import run, run_with


def test_seven_and_three():
    """Prints a real return of 3.88% and a rough guess of 4.00%."""
    printed = run()
    expected = "Real return: 3.88%\nRough guess: 4.00%\n"
    assert printed == expected, f"Expected this:\n{expected}\nYour program printed:\n{printed}"


def test_any_rates():
    """Works for any rates: 10% in a year of 8% inflation is a real 1.85%, roughly 2.00%."""
    printed = run_with({"nominal": 0.10, "inflation": 0.08})
    expected = "Real return: 1.85%\nRough guess: 2.00%\n"
    assert printed == expected, (
        f"With nominal = 0.10 and inflation = 0.08 it should print:\n{expected}\nIt printed:\n{printed}"
    )
