import numpy as np

from checks import function, run


def test_the_output():
    """Prints (6, 3) and the first two rows."""
    printed = run()
    assert printed == "(6, 3)\n[[0. 0. 1.]\n [1. 0. 1.]]\n", f"Your program printed:\n{printed}"


def test_other_points():
    """Four points give a 4-by-3 matrix whose last column is ones."""
    design = function("design")
    A = design(np.array([[1.0, 2.0, 9.0], [3.0, 4.0, 9.0], [5.0, 6.0, 9.0], [7.0, 8.0, 9.0]]))
    assert A.shape == (4, 3)
    assert A[:, 2].tolist() == [1.0, 1.0, 1.0, 1.0]
    assert A[:, 0].tolist() == [1.0, 3.0, 5.0, 7.0]
