from checks import run

EXPECTED = "Welcome aboard!\nPlease find your seat.\nWe leave in five minutes.\n"


def test_announcement():
    """Prints the three lines of the announcement."""
    printed = run()
    assert printed == EXPECTED, (
        f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"
    )
