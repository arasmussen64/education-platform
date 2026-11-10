from checks import run, run_with

EXPECTED = "[3.0, 2.0]\n"


def test_three_points():
    """Prints [3.0, 2.0]."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_points():
    """Works for any points, in any number of dimensions: two 3-D points give [3.0, 3.0, 3.0]."""
    printed = run_with({"points": [[2, 2, 2], [4, 4, 4]]})
    assert printed == "[3.0, 3.0, 3.0]\n", (
        f"With [[2, 2, 2], [4, 4, 4]] it should print [3.0, 3.0, 3.0]. It printed:\n{printed}"
    )
