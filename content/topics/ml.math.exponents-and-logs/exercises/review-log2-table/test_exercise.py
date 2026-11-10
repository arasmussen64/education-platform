from checks import run, run_with


def test_the_table():
    """Prints the five rows, the log going up by 1 each time the number doubles."""
    assert run() == "1 0.0\n2 1.0\n4 2.0\n8 3.0\n16 4.0\n"


def test_other_numbers():
    """Works for other numbers: 32 and 1024 give 5.0 and 10.0."""
    assert run_with({"numbers": [32, 1024]}) == "32 5.0\n1024 10.0\n"
