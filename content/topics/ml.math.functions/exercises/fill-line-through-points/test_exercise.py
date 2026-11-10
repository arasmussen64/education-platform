from checks import run, run_with


def test_these_points():
    """Prints y = 3.0x + 4.0."""
    printed = run()
    assert printed == "y = 3.0x + 4.0\n", f"Your program printed:\n{printed}"


def test_any_points():
    """Works for any two points: (0, 2) and (4, 10) give y = 2.0x + 2.0."""
    printed = run_with({"x1": 0, "y1": 2, "x2": 4, "y2": 10})
    assert printed == "y = 2.0x + 2.0\n", (
        f"Through (0, 2) and (4, 10) it should print y = 2.0x + 2.0. It printed:\n{printed}"
    )
