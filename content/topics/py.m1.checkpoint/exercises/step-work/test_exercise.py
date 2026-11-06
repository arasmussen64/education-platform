from checks import run


def test_receipt():
    """Typing 18, 4 and 20 prints the receipt."""
    printed = run("18\n4\n20\n")
    expected = "Subtotal: $22.00\nTip (20%): $4.40\nTotal: $26.40\n"
    assert printed == expected, f"Your program printed:\n{printed}"


def test_with_decimals():
    """Works with decimals too: 12.25, 3.5 and 15."""
    printed = run("12.25\n3.5\n15\n")
    expected = "Subtotal: $15.75\nTip (15%): $2.36\nTotal: $18.11\n"
    assert printed == expected, f"Your program printed:\n{printed}"
