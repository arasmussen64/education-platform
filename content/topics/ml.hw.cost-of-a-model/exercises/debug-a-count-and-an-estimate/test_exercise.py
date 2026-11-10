from checks import function, run

EXPECTED = 'parameters: 235,146\none epoch at 30 percent of 10 TFLOP/s: 28.2 ms\n'


def test_the_output():
    """Prints the right count and the right estimate."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_values():
    """[4, 3, 2] has 23 parameters, and halving the utilization doubles the time."""
    parameter_count = function("parameter_count")
    training_seconds = function("training_seconds")
    assert parameter_count([4, 3, 2]) == 23
    assert abs(training_seconds(1e12, 1e12, 0.5) - 2 * training_seconds(1e12, 1e12, 1.0)) < 1e-9
