from checks import run, run_with


def test_three_values():
    """Prints 5 for [7, 1, 5]."""
    assert run() == "5\n"


def test_five_values():
    """Prints 5 for [3, 9, 1, 7, 5], the middle once sorted."""
    assert run_with({"values": [3, 9, 1, 7, 5]}) == "5\n"
