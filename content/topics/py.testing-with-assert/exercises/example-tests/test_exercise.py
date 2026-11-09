from checks import function, run


def test_program():
    """Run directly, the file prints that all checks passed."""
    assert run() == "square: all checks passed\n"


def test_pieces():
    """square(5) returns 25, and test_square() runs without a failure."""
    assert function("square")(5) == 25
    function("test_square")()
