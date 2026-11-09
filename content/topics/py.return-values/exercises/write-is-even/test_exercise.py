from checks import function, printed, run


def test_returns_bool():
    """is_even(4) returns True, is_even(7) returns False, is_even(0) returns True."""
    is_even = function("is_even")
    assert is_even(4) is True, f"is_even(4) returned {is_even(4)!r}"
    assert is_even(7) is False, f"is_even(7) returned {is_even(7)!r}"
    assert is_even(0) is True, f"is_even(0) returned {is_even(0)!r}"


def test_prints_nothing():
    """is_even prints nothing: it returns the answer."""
    assert printed(function("is_even"), 4) == "", "is_even should return, not print"


def test_program():
    """Running the program prints True, then False."""
    got = run()
    assert got == "True\nFalse\n", f"Your program printed:\n{got}"
