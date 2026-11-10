from checks import function, run


def test_the_output():
    """Prints the four bit strings."""
    assert run() == '00100101 0101 000 11111111\n'


def test_against_format():
    """Agrees with format(n, '010b') for 0 to 1023."""
    to_binary = function("to_binary")
    assert all(to_binary(n, 10) == format(n, "010b") for n in range(1024))
