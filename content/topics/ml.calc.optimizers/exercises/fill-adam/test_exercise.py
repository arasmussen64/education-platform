from checks import function, run


def test_the_output():
    """Prints the two paths."""
    printed = run()
    assert printed == '[1.9, 1.8002, 1.7006]\n[-49.9, -49.8, -49.7]\n', f"Your program printed:\n{printed}"


def test_first_step_is_the_rate():
    """From any start the first step has size exactly the rate, against the gradient."""
    adam_steps = function("adam_steps")
    assert adam_steps(7.0, 0.25, 1) == [6.75]
    assert adam_steps(-3.0, 0.01, 1) == [-2.99]
