from checks import function, run


def test_program():
    """Running the program prints 120.0."""
    got = run()
    assert got == "120.0\n", f"Your program printed:\n{got}"


def test_any_rate():
    """total_with_tax(50, 0.5) returns 75.0: the rate comes from the call, not from outside."""
    total_with_tax = function("total_with_tax")
    assert total_with_tax(50, 0.5) == 75.0, (
        f"total_with_tax(50, 0.5) returned {total_with_tax(50, 0.5)!r}"
    )
