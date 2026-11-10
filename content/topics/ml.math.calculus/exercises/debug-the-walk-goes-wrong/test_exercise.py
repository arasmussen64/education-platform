from checks import run, run_with


def test_from_zero():
    """Prints 3.0."""
    printed = run()
    assert printed == "3.0\n", f"Your program printed:\n{printed}"


def test_from_ten():
    """From x = 10, further away, thirty steps end at 3.01."""
    printed = run_with({"x": 10})
    assert printed == "3.01\n", f"From x = 10 it should print 3.01. It printed:\n{printed}"
