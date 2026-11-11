from checks import function, run


def test_largest():
    """largest returns the bigger number whichever side it's on: largest(3, 8) is 8."""
    largest = function("largest")
    assert largest(3, 8) == 8, f"largest(3, 8) returned {largest(3, 8)!r}"
    assert largest(9, 2) == 9, f"largest(9, 2) returned {largest(9, 2)!r}"


def test_sum_to():
    """sum_to(4) returns 10, which is 1 + 2 + 3 + 4."""
    sum_to = function("sum_to")
    assert sum_to(4) == 10, f"sum_to(4) returned {sum_to(4)!r}"
    assert sum_to(1) == 1, f"sum_to(1) returned {sum_to(1)!r}"


def test_half():
    """half(10) returns 5.0."""
    half = function("half")
    assert half(10) == 5.0, f"half(10) returned {half(10)!r}"


def test_program():
    """Running the program prints 8, 9, 10 and 5.0."""
    got = run()
    assert got == "8\n9\n10\n5.0\n", f"Your program printed:\n{got}"
