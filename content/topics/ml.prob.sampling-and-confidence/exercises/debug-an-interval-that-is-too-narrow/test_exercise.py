import numpy as np

from checks import function, run

EXPECTED = 'interval 95.9 106.5\ncoverage 0.937\n'


def test_the_output():
    """Prints the interval and the coverage."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_interval_on_a_known_sample():
    """For [2, 4, 4, 4, 5, 5, 7, 9] the interval is 5 plus or minus 1.96 times 0.756."""
    interval = function("interval")
    low, high = interval(np.array([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]))
    assert abs(low - (5 - 1.96 * 0.756)) < 0.002 and abs(high - (5 + 1.96 * 0.756)) < 0.002
