from checks import function, run


def test_program():
    """Prints the price line, then the total line."""
    assert run() == "Price: $20.00\nTotal: $22.00\n"


def test_pieces():
    """Each worker returns its result and has a docstring."""
    total_with_tax = function("total_with_tax")
    receipt_line = function("receipt_line")
    assert total_with_tax(100, 0.5) == 150.0
    assert receipt_line("Tax", 2) == "Tax: $2.00"
    assert (total_with_tax.__doc__ or "").strip() != ""
    assert (receipt_line.__doc__ or "").strip() != ""
