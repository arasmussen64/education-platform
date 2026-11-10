import numpy as np

from checks import function, run


def test_the_output():
    """Prints the sheared square's corners."""
    printed = run()
    assert printed == "[[0. 0.]\n [1. 0.]\n [2. 1.]\n [1. 1.]]\n", f"Your program printed:\n{printed}"


def test_other_matrix_and_points():
    """A scaling by 2 and 3 of two points gives each point scaled, as rows."""
    transform = function("transform")
    M = np.array([[2.0, 0.0], [0.0, 3.0]])
    points = np.array([[1.0, 1.0], [-1.0, 0.5]])
    assert transform(M, points).tolist() == [[2.0, 3.0], [-2.0, 1.5]]
