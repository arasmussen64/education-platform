import numpy as np

from checks import function, run


def test_the_output():
    """Prints [2. 6.]."""
    assert run() == '[2. 6.]\n'


def test_another_point_and_function():
    """f = x y at (2, 3) gives [3, 2] to six decimals."""
    numeric_gradient = function("numeric_gradient")
    g = numeric_gradient(lambda p: p[0] * p[1], np.array([2.0, 3.0]))
    assert np.abs(g - [3.0, 2.0]).max() < 1e-6
