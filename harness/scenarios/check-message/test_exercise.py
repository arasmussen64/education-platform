from solution import double


def test_doubles():
    """Doubles a number."""
    got = double(2)
    assert got == 4, f"double(2) should be 4, but it returned {got}"


def test_zero():
    """Doubles zero."""
    assert double(0) == 0
