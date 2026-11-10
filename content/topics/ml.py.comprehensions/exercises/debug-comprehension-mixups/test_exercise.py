from checks import run, run_with

EXPECTED = "[2, 8, 4]\n{'tea': 3, 'bread': 5}\n"


def test_the_output():
    """Prints [2, 8, 4], then {'tea': 3, 'bread': 5}."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_data():
    """Works for other numbers and words."""
    printed = run_with({"numbers": [1, 6], "words": ["x"]})
    assert printed == "[6]\n{'x': 1}\n", f"With [1, 6] and ['x'] it should print [6], then {{'x': 1}}. It printed:\n{printed}"
