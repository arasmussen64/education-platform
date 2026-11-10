import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three stride tuples."""
    assert run() == '(32, 8) (20, 4) (24, 8, 2)\n'


def test_against_numpy():
    """Matches NumPy for a one-axis and a four-axis array."""
    c_strides = function("c_strides")
    for shape in ((9,), (2, 3, 4, 5)):
        assert c_strides(shape, 8) == np.zeros(shape, dtype=np.float64).strides
