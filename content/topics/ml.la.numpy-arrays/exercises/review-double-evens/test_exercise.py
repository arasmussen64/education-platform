import numpy as np

from checks import function, run


def test_the_output():
    """Prints [ 4  8 12]."""
    assert run() == "[ 4  8 12]\n"


def test_other_values():
    """Keeps only the evens, doubled; an array with no evens gives an empty array."""
    double_evens = function("double_evens")
    assert double_evens(np.array([7, 10])).tolist() == [20]
    assert double_evens(np.array([1, 3])).tolist() == []
