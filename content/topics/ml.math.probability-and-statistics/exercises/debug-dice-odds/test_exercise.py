from checks import run, run_with

EXPECTED = "Ways: 6\nChance: 16.7%\n"


def test_at_least_ten():
    """Prints Ways: 6, then Chance: 16.7%."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_any_target():
    """Works for any target: at least 11 is 3 ways, 8.3%."""
    printed = run_with({"target": 11})
    assert printed == "Ways: 3\nChance: 8.3%\n", (
        f"With target = 11 it should print Ways: 3, then Chance: 8.3%. It printed:\n{printed}"
    )
