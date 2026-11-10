import numpy as np

from checks import function, run


def test_the_output():
    """Prints the standard error and the two intervals."""
    printed = run()
    assert printed == '2.989\n(74.14, 85.86)\n(77.19, 82.81)\n', f"Your program printed:\n{printed}"


def test_known_values():
    """[2, 4, 4, 4, 5, 5, 7, 9] has sample standard deviation 2.138 and standard error 0.756; z = 1 gives an interval one standard error wide each way."""
    standard_error = function("standard_error")
    confidence_interval = function("confidence_interval")
    sample = np.array([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    assert abs(standard_error(sample) - 0.756) < 0.001
    low, high = confidence_interval(sample, z=1)
    assert abs(low - 4.24) < 0.01 and abs(high - 5.76) < 0.01
