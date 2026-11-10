import numpy as np

from checks import function, run


def test_the_output():
    """Prints [4. 3.]."""
    assert run() == "[4. 3.]\n"


def test_other_matrix():
    """A stretch by 2 along x sends [1, 1] to [2, 1]."""
    apply = function("apply")
    assert apply(np.array([[2.0, 0.0], [0.0, 1.0]]), np.array([1.0, 1.0])).tolist() == [2.0, 1.0]
