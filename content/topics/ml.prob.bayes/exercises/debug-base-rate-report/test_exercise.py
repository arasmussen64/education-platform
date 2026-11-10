from checks import function, run

EXPECTED = 'positives 950 9900\nafter one positive 0.088\nafter two positives 0.477\n'


def test_the_output():
    """Prints the positives and the chance after one and two positive tests."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_table_on_other_numbers():
    """A perfectly specific test has no false positives; a useless one flags everyone."""
    table = function("table")
    assert table(1000, 0.1, 0.9, 1.0) == (90.0, 0.0)
    assert table(1000, 0.1, 0.9, 0.0) == (90.0, 900.0)
