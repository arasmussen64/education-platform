import numpy as np

from checks import function, run


def test_this_array():
    """Prints [0.   0.25 0.5  1.  ]."""
    printed = run()
    assert printed == "[0.   0.25 0.5  1.  ]\n", f"Your program printed:\n{printed}"


def test_other_arrays():
    """The smallest value becomes 0 and the largest 1, for other arrays too."""
    normalize = function("normalize")
    assert normalize(np.array([5.0, 10.0])).tolist() == [0.0, 1.0]
    assert normalize(np.array([3, 3, 9])).tolist() == [0.0, 0.0, 1.0]
