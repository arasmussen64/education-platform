from checks import run, run_with


def test_this_sum():
    """Prints [5, 3, -3]."""
    assert run() == "[5, 3, -3]\n"


def test_another_sum():
    """[1, 1] plus [2, 3] is [3, 4]."""
    assert run_with({"a": [1, 1], "b": [2, 3]}) == "[3, 4]\n"
