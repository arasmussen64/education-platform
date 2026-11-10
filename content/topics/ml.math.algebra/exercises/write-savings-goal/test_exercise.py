from checks import run, run_with


def test_this_goal():
    """Prints Months: 6.0."""
    printed = run()
    assert printed == "Months: 6.0\n", f"Your program printed:\n{printed}"


def test_any_goal():
    """Works for any numbers: 100 saved, a goal of 1000 and 80 a month is 11.2 months."""
    printed = run_with({"saved": 100, "goal": 1000, "monthly": 80})
    assert printed == "Months: 11.2\n", (
        f"With saved 100, goal 1000 and monthly 80 it should print Months: 11.2. It printed:\n{printed}"
    )
