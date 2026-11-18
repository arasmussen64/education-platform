from checks import run, run_with

EXPECTED = (
    "ABC: spread 0.04, 0.16% of the middle\n"
    "TINY: spread 0.20, 6.25% of the middle\n"
    "BIG: spread 1.00, 0.67% of the middle\n"
)


def test_the_report():
    """Prints each stock's spread, and the spread as a percentage of the middle price."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_quotes():
    """Works for other quotes: bid 9.90 and ask 10.10 is a spread of 0.20, 2.00% of the middle."""
    printed = run_with({"quotes": {"Q1": {"bid": 9.90, "ask": 10.10}, "Q2": {"bid": 59.97, "ask": 60.03}}})
    expected = "Q1: spread 0.20, 2.00% of the middle\nQ2: spread 0.06, 0.10% of the middle\n"
    assert printed == expected, f"With other quotes it should print:\n{expected}\nIt printed:\n{printed}"
