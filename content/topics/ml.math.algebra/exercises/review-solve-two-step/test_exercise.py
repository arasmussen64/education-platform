from checks import run, run_with


def test_this_equation():
    """Prints x = 5.0, then check: 29.0."""
    assert run() == "x = 5.0\ncheck: 29.0\n"


def test_any_equation():
    """Works for any a, b and c: 3x + 2 = 14 gives 4.0."""
    assert run_with({"a": 3, "b": 2, "c": 14}) == "x = 4.0\ncheck: 14.0\n"
