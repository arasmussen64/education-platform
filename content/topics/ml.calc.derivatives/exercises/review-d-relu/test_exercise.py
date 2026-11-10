import numpy as np

from checks import function, run


def test_the_output():
    """Prints [0. 1. 1.]."""
    assert run() == '[0. 1. 1.]\n'


def test_other_inputs():
    """Zero on the left, one on the right, as floats, for another array."""
    d_relu = function("d_relu")
    assert d_relu(np.array([-0.5, -2.0, 4.0, 0.1])).tolist() == [0.0, 0.0, 1.0, 1.0]
    assert str(d_relu(np.array([7.0, -7.0]))) == "[1. 0.]"
