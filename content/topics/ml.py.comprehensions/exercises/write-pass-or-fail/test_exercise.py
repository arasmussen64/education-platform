from checks import run, run_with


def test_these_scores():
    """Prints {'Ada': 'pass', 'Bob': 'fail', 'Cy': 'pass'}."""
    printed = run()
    assert printed == "{'Ada': 'pass', 'Bob': 'fail', 'Cy': 'pass'}\n", f"Your program printed:\n{printed}"


def test_other_scores():
    """Works for other scores: 49 fails and 50 passes."""
    printed = run_with({"scores": {"Dee": 49, "Eve": 50}})
    assert printed == "{'Dee': 'fail', 'Eve': 'pass'}\n", (
        f"With Dee 49 and Eve 50 it should print {{'Dee': 'fail', 'Eve': 'pass'}}. It printed:\n{printed}"
    )
