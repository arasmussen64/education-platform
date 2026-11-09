from checks import function, printed, run


def test_program():
    """Running the program prints 46."""
    got = run()
    assert got == "46\n", f"Your program printed:\n{got}"


def test_area_returns():
    """area(5, 5) returns 25 and prints nothing."""
    area = function("area")
    assert area(5, 5) == 25, f"area(5, 5) returned {area(5, 5)!r}"
    assert printed(area, 5, 5) == "", "area should return the value, not print it"
