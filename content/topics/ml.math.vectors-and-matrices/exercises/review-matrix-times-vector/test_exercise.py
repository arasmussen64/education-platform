from checks import run, run_with


def test_this_product():
    """Prints [8, 19]."""
    assert run() == "[8, 19]\n"


def test_another_product():
    """[[1, 2], [3, 4]] times [5, 6] is [17, 39]."""
    assert run_with({"m": [[1, 2], [3, 4]], "v": [5, 6]}) == "[17, 39]\n"
