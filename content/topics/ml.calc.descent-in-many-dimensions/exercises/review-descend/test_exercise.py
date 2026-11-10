import numpy as np

from checks import function, run


def test_the_output():
    """Prints [0.5  0.25]."""
    assert run() == '[0.5  0.25]\n'


def test_other_runs():
    """Ten steps at rate 0.1 on x² + y² from (1, 1) give (0.8 ** 10, 0.8 ** 10); zero steps give the start."""
    descend = function("descend")
    assert np.allclose(descend(lambda p: 2 * p, np.array([1.0, 1.0]), 0.1, 10), [0.8**10, 0.8**10])
    assert np.allclose(descend(lambda p: 2 * p, np.array([1.0, 1.0]), 0.1, 0), [1.0, 1.0])
