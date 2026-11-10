from checks import function, run


def test_the_output():
    """Prints [1, 4, 9, 16]."""
    assert run() == "[1, 4, 9, 16]\n"


def test_other_counts():
    """first_squares(0) yields nothing, and next() on first_squares(2) gives 1."""
    first_squares = function("first_squares")
    assert list(first_squares(0)) == []
    assert next(first_squares(2)) == 1
