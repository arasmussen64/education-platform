import numpy as np

from checks import function, run


def test_the_output():
    """Prints 13.445067."""
    assert run() == '13.445067\n'


def test_other_points():
    """At 0 the derivative is 3, and at 1 it matches a central difference."""
    chain_derivative = function("chain_derivative")
    assert abs(chain_derivative(0.0) - 3.0) < 1e-9
    numeric = (np.exp(3 * (1 + 1e-6)) - np.exp(3 * (1 - 1e-6))) / 2e-6
    assert abs(chain_derivative(1.0) - numeric) < 1e-5
