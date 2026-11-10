from checks import run

EXPECTED = 'counts of 3 and 200: 160 120\ndark pixels: 160\n'


def test_the_output():
    """Prints 160 and 120 for the two counts, and 160 dark pixels."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"
