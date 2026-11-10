import numpy as np

from checks import function, run


def test_the_output():
    """Prints True, True, False."""
    assert run() == "True\nTrue\nFalse\n"


def test_other_pairs():
    """Works for a diagonal matrix: [0, 1] with 3 is a pair, [1, 1] with 3 is not."""
    is_eigenpair = function("is_eigenpair")
    D = np.array([[2.0, 0.0], [0.0, 3.0]])
    assert is_eigenpair(D, np.array([0.0, 1.0]), 3.0) is True
    assert is_eigenpair(D, np.array([1.0, 1.0]), 3.0) is False
