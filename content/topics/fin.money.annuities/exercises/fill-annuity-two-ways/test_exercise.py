from checks import run, run_with


def test_both_ways():
    """Prints 5,310.85 by the loop and by the formula."""
    expected = "By loop: 5,310.85\nBy formula: 5,310.85\n"
    printed = run()
    assert printed == expected, f"Expected this:\n{expected}\nYour program printed:\n{printed}"


def test_other_payments():
    """Works for other payments: 12 payments of 250 at 2% a month are worth 2,643.84."""
    expected = "By loop: 2,643.84\nBy formula: 2,643.84\n"
    printed = run_with({"rate": 0.02, "months": 12})
    assert printed == expected, (
        f"With rate = 0.02 and months = 12 it should print:\n{expected}\nIt printed:\n{printed}"
    )
