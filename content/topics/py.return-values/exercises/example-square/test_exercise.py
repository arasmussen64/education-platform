from checks import function, run


def test_program():
    """Prints 9, the area sentence, and 16."""
    assert run() == "9\nA 4 by 4 square has area 16\n16\n"


def test_square_returns():
    """square(5) returns 25."""
    assert function("square")(5) == 25
