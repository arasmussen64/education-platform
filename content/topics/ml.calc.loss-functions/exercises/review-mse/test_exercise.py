import numpy as np

from checks import function, run


def test_the_output():
    """Prints 0.1375."""
    assert run() == '0.1375\n'


def test_other_values():
    """Misses of 1, 2 and 3 average to 14/3; equal arrays give 0."""
    mse = function("mse")
    assert abs(mse(np.array([1.0, 2.0, 3.0]), np.array([0.0, 0.0, 0.0])) - 14 / 3) < 1e-12
    assert mse(np.array([5.0, 5.0]), np.array([5.0, 5.0])) == 0
