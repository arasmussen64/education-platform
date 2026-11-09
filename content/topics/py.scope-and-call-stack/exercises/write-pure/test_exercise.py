from checks import function, printed


def test_quarter_off():
    """apply_discount(100, 25) returns 75.0."""
    apply_discount = function("apply_discount")
    assert apply_discount(100, 25) == 75.0, (
        f"apply_discount(100, 25) returned {apply_discount(100, 25)!r}"
    )


def test_any_values():
    """apply_discount(80, 10) returns 72.0, and apply_discount(19.99, 15) returns 16.99."""
    apply_discount = function("apply_discount")
    assert apply_discount(80, 10) == 72.0, (
        f"apply_discount(80, 10) returned {apply_discount(80, 10)!r}"
    )
    assert apply_discount(19.99, 15) == 16.99, (
        f"apply_discount(19.99, 15) returned {apply_discount(19.99, 15)!r}"
    )


def test_returns_quietly():
    """apply_discount prints nothing."""
    assert printed(function("apply_discount"), 10, 10) == ""
