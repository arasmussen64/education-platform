from checks import run


def test_the_walkthrough():
    """Prints 10, 20, the countdown 3 2 1, then 14 and an empty list."""
    assert run() == "10\n20\n3\n2\n1\n14\n[]\n"
