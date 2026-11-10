import numpy as np

from checks import function, run


def test_the_output():
    """Prints the two standard errors."""
    assert run() == '2.989\n1.436\n'


def test_a_known_sample():
    """[2, 4, 4, 4, 5, 5, 7, 9] has standard error 0.756."""
    standard_error = function("standard_error")
    assert abs(standard_error(np.array([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])) - 0.756) < 0.001
