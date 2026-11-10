from checks import run, run_with


def test_from_zero():
    """Prints Stopped at 2.995 after 29 steps."""
    printed = run()
    assert printed == "Stopped at 2.995 after 29 steps\n", f"Your program printed:\n{printed}"


def test_from_ten():
    """From x = 10.0 it stops at 3.004 after 33 steps."""
    printed = run_with({"x": 10.0})
    assert printed == "Stopped at 3.004 after 33 steps\n", (
        f"From x = 10.0 it should print Stopped at 3.004 after 33 steps. It printed:\n{printed}"
    )
