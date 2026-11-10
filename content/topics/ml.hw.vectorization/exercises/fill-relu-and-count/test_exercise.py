import numpy as np

from checks import function, run


def test_the_output():
    """Prints the rectified array and the count."""
    printed = run()
    assert printed == '[0.  0.  0.  1.5 3.  0. ] 2\n', f"Your program printed:\n{printed}"


def test_more_values():
    """relu keeps positives, zeroes the rest, and works on a matrix; count_positive is 0 for all-negative input."""
    relu = function("relu")
    count_positive = function("count_positive")
    assert relu(np.array([[-1.0, 2.0], [3.0, -4.0]])).tolist() == [[0.0, 2.0], [3.0, 0.0]]
    assert count_positive(np.array([-1.0, -2.0, 0.0])) == 0 and count_positive(np.array([0.5, 1e-9])) == 2
