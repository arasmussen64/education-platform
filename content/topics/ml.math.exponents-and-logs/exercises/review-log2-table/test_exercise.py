from checks import run


def test_the_table():
    """Prints the five rows, the log going up by 1 each time the number doubles."""
    assert run() == "1 0.0\n2 1.0\n4 2.0\n8 3.0\n16 4.0\n"
