from checks import run


def test_matches_the_table():
    """Prints 6 4, then 19, as the table says."""
    printed = run()
    assert printed == "6 4\n19\n", f"Your program printed:\n{printed}"
