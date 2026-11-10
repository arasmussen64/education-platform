from checks import run


def test_evaluates_and_tabulates():
    """Prints 7, 1 and -3, then the table from 0 to 3."""
    assert run() == "7\n1\n-3\n0 1\n1 3\n2 5\n3 7\n"
