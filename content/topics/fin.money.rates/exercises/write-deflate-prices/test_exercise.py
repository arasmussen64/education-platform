from checks import function, run

EXPECTED = (
    "2000: $5.40 then, $10.10 in 2025 money\n"
    "2010: $7.90 then, $11.66 in 2025 money\n"
    "2020: $9.20 then, $11.44 in 2025 money\n"
    "2025: $11.00 then, $11.00 in 2025 money\n"
)


def test_the_table():
    """Prints each ticket price then and in 2025 money."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_prices():
    """in_2025_dollars(100, 1995) is about 211.25, and in_2025_dollars(50, 2015) about 67.92."""
    in_2025_dollars = function("in_2025_dollars")
    got = in_2025_dollars(100, 1995)
    assert abs(got - 211.2487) < 0.005, f"in_2025_dollars(100, 1995) returned {got}; expected about 211.25."
    got = in_2025_dollars(50, 2015)
    assert abs(got - 67.9156) < 0.005, f"in_2025_dollars(50, 2015) returned {got}; expected about 67.92."
