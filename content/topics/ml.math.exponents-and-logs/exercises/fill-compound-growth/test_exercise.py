from checks import run, run_with


def test_ten_years():
    """Prints After 10 years: 1628.89."""
    printed = run()
    assert printed == "After 10 years: 1628.89\n", f"Your program printed:\n{printed}"


def test_any_growth():
    """Works for any start, rate and years: 500 at 10% for 3 years is 665.50."""
    printed = run_with({"start": 500, "rate": 10, "years": 3})
    assert printed == "After 3 years: 665.50\n", (
        f"With 500, 10% and 3 years it should print After 3 years: 665.50. It printed:\n{printed}"
    )
