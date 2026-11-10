from checks import run, run_with

EXPECTED = "Ada 30.0\nBo 0\nCy 0\n"


def test_the_output():
    """Prints each user's name and total."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_users():
    """Works for other users, including one with no orders key."""
    printed = run_with({"text": '[{"name": "Di", "orders": [{"total": 2}]}, {"name": "Ed"}]'})
    assert printed == "Di 2\nEd 0\n", f"With Di and Ed it printed:\n{printed}"
