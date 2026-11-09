from checks import function, printed


def test_divides():
    """safe_divide(6, 3) returns 2.0, and safe_divide(1, 4) returns 0.25."""
    safe_divide = function("safe_divide")
    assert safe_divide(6, 3) == 2.0, f"safe_divide(6, 3) returned {safe_divide(6, 3)!r}"
    assert safe_divide(1, 4) == 0.25, f"safe_divide(1, 4) returned {safe_divide(1, 4)!r}"


def test_zero():
    """safe_divide(1, 0) returns None instead of crashing, and prints nothing."""
    safe_divide = function("safe_divide")
    assert safe_divide(1, 0) is None, f"safe_divide(1, 0) returned {safe_divide(1, 0)!r}"
    assert printed(safe_divide, 1, 0) == "", "safe_divide should not print"
