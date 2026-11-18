from checks import run, run_with

EXPECTED = (
    "Year 0: 3,000.00\n"
    "Year 1: 3,150.00\n"
    "Year 2: 3,307.50\n"
    "Year 3: 3,472.88\n"
    "Year 4: 3,646.52\n"
)


def test_the_table():
    """Prints the five rows, from Year 0: 3,000.00 to Year 4: 3,646.52."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_savings():
    """Works for other numbers: 1,000,000 at 10% for 2 years ends at 1,210,000.00."""
    expected = "Year 0: 1,000,000.00\nYear 1: 1,100,000.00\nYear 2: 1,210,000.00\n"
    printed = run_with({"savings": 1000000, "rate": 0.1, "years": 2})
    assert printed == expected, (
        f"With savings = 1000000, rate = 0.1 and years = 2 it should print:\n{expected}\n"
        f"It printed:\n{printed}"
    )
