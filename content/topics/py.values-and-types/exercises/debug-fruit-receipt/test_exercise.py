from checks import run

EXPECTED = "Apples: 3\nPears: 2\nFruit in the bag: 5\nBags: 2\n"


def test_receipt():
    """Prints the receipt, with the right totals."""
    printed = run()
    assert printed == EXPECTED, (
        f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"
    )
