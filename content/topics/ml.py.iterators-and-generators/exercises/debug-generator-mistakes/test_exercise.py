from checks import function, run

EXPECTED = "[1, 4, 9, 16]\n30\n16\n"


def test_the_output():
    """Prints the squares, their total and their largest."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_squares_is_a_generator():
    """squares(3) gives its squares one at a time to next(): 1, then 4, then 9."""
    squares = function("squares")
    g = squares(3)
    assert next(g) == 1
    assert next(g) == 4
    assert list(g) == [9]
