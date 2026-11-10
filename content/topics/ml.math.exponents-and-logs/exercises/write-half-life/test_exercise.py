from checks import function, run

TABLE = "0 h: 200.0 mg\n6 h: 100.0 mg\n12 h: 50.0 mg\n18 h: 25.0 mg\n24 h: 12.5 mg\n"


def test_the_function():
    """remaining(6) is 100.0, and remaining(3) is about 141.4."""
    remaining = function("remaining")
    assert remaining(6) == 100.0, f"remaining(6) returned {remaining(6)}"
    assert round(remaining(3), 1) == 141.4, f"remaining(3) returned {remaining(3)}"


def test_the_table():
    """Prints the five rows from 0 h to 24 h."""
    printed = run()
    assert printed == TABLE, f"Expected this:\n{TABLE}\nYour program printed:\n{printed}"
