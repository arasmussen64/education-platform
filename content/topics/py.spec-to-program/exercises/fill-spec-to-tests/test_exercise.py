from checks import function, run


def test_shipping():
    """shipping follows the spec: 5.0 up to 1 kg, then 2.0 per started kilogram."""
    shipping = function("shipping")
    for weight, expected in [(0.5, 5.0), (1, 5.0), (1.2, 7.0), (2, 7.0), (2.5, 9.0), (3, 9.0)]:
        got = shipping(weight)
        assert got == expected, f"shipping({weight}) returned {got!r}, not {expected!r}"


def test_tests():
    """test_shipping passes: its expected values match the spec."""
    try:
        function("test_shipping")()
    except AssertionError:
        raise AssertionError("an assert in test_shipping fails; check the expected values against the spec")


def test_program():
    """Running the program prints the tests' message and the price of a 2.5 kg parcel."""
    got = run()
    assert got == "shipping: all checks passed\n2.5 kg: 9.00\n", f"Your program printed:\n{got}"
