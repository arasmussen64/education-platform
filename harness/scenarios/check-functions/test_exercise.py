from checks import function, printed, run


def test_greet():
    """greet("Ada") prints Hello, Ada!"""
    assert printed(function("greet"), "Ada") == "Hello, Ada!\n"


def test_default():
    """A second argument replaces Hello."""
    assert printed(function("greet"), "Bob", "Hi") == "Hi, Bob!\n"


def test_double():
    """double(4) returns 8."""
    assert function("double")(4) == 8


def test_program():
    """Running the program greets Ada."""
    assert run() == "Hello, Ada!\n"


def test_missing():
    """A function that is not there fails with a plain message."""
    function("triple")
