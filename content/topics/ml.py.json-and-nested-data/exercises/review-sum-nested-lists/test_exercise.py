from checks import run, run_with


def test_this_data():
    """Prints 6."""
    assert run() == "6\n"


def test_other_data():
    """Prints 9 for {"x": [], "y": [4, 5]}."""
    assert run_with({"data": {"x": [], "y": [4, 5]}}) == "9\n"
