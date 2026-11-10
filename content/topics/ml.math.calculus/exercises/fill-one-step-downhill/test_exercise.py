from checks import run, run_with


def test_from_zero():
    """Prints 0.6."""
    printed = run()
    assert printed == "0.6\n", f"Your program printed:\n{printed}"


def test_from_the_other_side():
    """From x = 5 the step goes left, to 4.6."""
    printed = run_with({"x": 5})
    assert printed == "4.6\n", f"From x = 5 it should print 4.6. It printed:\n{printed}"
