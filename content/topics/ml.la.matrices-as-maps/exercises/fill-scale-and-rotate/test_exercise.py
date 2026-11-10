import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three transformed vectors."""
    printed = run()
    assert printed == "[-1.  0.]\n[3.  0.5]\n[-2.  0.]\n", f"Your program printed:\n{printed}"


def test_the_matrices():
    """rotation(45) sends [1, 0] to [0.7071, 0.7071]; scaling(2, 3) has determinant 6."""
    rotation = function("rotation")
    scaling = function("scaling")
    assert np.round(rotation(45) @ np.array([1.0, 0.0]), 4).tolist() == [0.7071, 0.7071]
    assert round(float(np.linalg.det(scaling(2, 3))), 6) == 6.0
