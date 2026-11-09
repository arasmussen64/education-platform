from checks import run, run_with


def test_from_three():
    """Prints 3, 2, 1, then Liftoff!"""
    assert run() == "3\n2\n1\nLiftoff!\n"


def test_from_zero():
    """With count starting at 0, the loop never runs: just Liftoff!"""
    assert run_with({"count": 0}) == "Liftoff!\n"
