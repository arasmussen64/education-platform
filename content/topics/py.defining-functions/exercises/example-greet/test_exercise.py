from checks import function, printed, run


def test_program():
    """Running the program greets Ada, then Bob."""
    assert run() == "Hello, Ada!\nHello, Bob!\n"


def test_greet_anyone():
    """greet("Cy") prints Hello, Cy!"""
    assert printed(function("greet"), "Cy") == "Hello, Cy!\n"
