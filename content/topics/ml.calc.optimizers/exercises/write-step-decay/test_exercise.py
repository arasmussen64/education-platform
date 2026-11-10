from checks import function, run


def test_the_output():
    """Prints the two lists of rates."""
    printed = run()
    assert printed == '[0.1, 0.1, 0.05, 0.05, 0.025, 0.025]\n[0.3, 0.15, 0.075, 0.009375]\n', f"Your program printed:\n{printed}"


def test_other_schedules():
    """A factor of 0.1 every 100 steps: step 99 keeps the start, step 100 is a tenth, step 250 a hundredth."""
    step_decay = function("step_decay")
    assert step_decay(1.0, 99, 100, 0.1) == 1.0
    assert abs(step_decay(1.0, 100, 100, 0.1) - 0.1) < 1e-12
    assert abs(step_decay(1.0, 250, 100, 0.1) - 0.01) < 1e-12
