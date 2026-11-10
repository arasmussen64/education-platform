from checks import run, run_with


def test_from_zero():
    """Prints 2.0, then 3.0."""
    assert run() == "2.0\n3.0\n"


def test_from_eight():
    """From x = 8.0 the steps go left: 6.0, then 5.0."""
    assert run_with({"x": 8.0}) == "6.0\n5.0\n"
