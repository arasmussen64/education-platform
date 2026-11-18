from checks import run, run_with

EXPECTED = (
    "Year 0: 2,400.00\n"
    "Year 1: 2,496.00\n"
    "Year 2: 2,595.84\n"
    "Year 3: 2,699.67\n"
    "Year 4: 2,807.66\n"
    "Year 5: 2,919.97\n"
)


def test_the_projection():
    """Prints six rows, from Year 0: 2,400.00 to Year 5: 2,919.97."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_numbers():
    """Works for other numbers: 10,000 at 10% for 3 years ends at 13,310.00."""
    expected = "Year 0: 10,000.00\nYear 1: 11,000.00\nYear 2: 12,100.00\nYear 3: 13,310.00\n"
    printed = run_with({"deposit": 10000, "rate": 0.1, "years": 3})
    assert printed == expected, (
        f"With deposit = 10000, rate = 0.1 and years = 3 it should print:\n{expected}\n"
        f"It printed:\n{printed}"
    )
