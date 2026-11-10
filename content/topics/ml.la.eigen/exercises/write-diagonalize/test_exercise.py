import numpy as np

from checks import function, run


def test_the_output():
    """Prints True twice."""
    printed = run()
    assert printed == "True\nTrue\n", f"Your program printed:\n{printed}"


def test_another_matrix():
    """D is diagonal, P D inv(P) rebuilds the matrix, and power(A, 3) is right, for a 3-by-3."""
    diagonalize = function("diagonalize")
    power = function("power")
    A = np.array([[2.0, 0.0, 1.0], [0.0, 3.0, 0.0], [1.0, 0.0, 2.0]])
    P, D = diagonalize(A)
    assert np.allclose(D, np.diag(np.diag(D)))
    assert np.allclose(P @ D @ np.linalg.inv(P), A)
    assert np.allclose(power(A, 3), np.linalg.matrix_power(A, 3))
