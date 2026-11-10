from checks import run, run_with


def test_this_line():
    """Prints the four rows for y = 2x - 3."""
    assert run() == "0 -3\n1 -1\n2 1\n3 3\n"


def test_any_line():
    """Works for any m and b: y = x gives 0 0, 1 1, 2 2, 3 3."""
    assert run_with({"m": 1, "b": 0}) == "0 0\n1 1\n2 2\n3 3\n"
