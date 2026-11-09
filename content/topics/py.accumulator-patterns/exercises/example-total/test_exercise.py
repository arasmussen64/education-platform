from checks import run


def test_two_numbers():
    """Typing 4, 6 and 0 prints 2 numbers, total 10."""
    assert run("4\n6\n0\n") == "2 numbers, total 10\n"


def test_none():
    """Typing 0 straight away prints 0 numbers, total 0."""
    assert run("0\n") == "0 numbers, total 0\n"
