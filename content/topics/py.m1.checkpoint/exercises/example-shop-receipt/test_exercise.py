from checks import run


def test_four_at_two_fifty():
    """4 at $2.50 with 10% off prints the receipt."""
    assert run("2.5\n4\n10\n") == (
        "Subtotal: $10.00\nDiscount (10%): -$1.00\nTotal: $9.00\n"
    )
