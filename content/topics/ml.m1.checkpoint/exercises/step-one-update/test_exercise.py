from checks import run, run_with


def test_one_step():
    """Prints 2.5 0.7."""
    printed = run()
    assert printed == "2.5 0.7\n", f"Your program printed:\n{printed}"


def test_a_smaller_rate():
    """With a rate of 0.01 the step is a fifth of the size: 0.5 0.14."""
    printed = run_with({"rate": 0.01})
    assert printed == "0.5 0.14\n", f"With rate = 0.01 it should print 0.5 0.14. It printed:\n{printed}"
