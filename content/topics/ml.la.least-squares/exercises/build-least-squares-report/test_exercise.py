import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

XS = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
A = np.column_stack([XS, np.ones(5)])
NOISY = np.array([3.2, 4.8, 7.1, 9.1, 10.8])
EXACT = 2 * XS + 1


def test_the_output():
    """Prints [1.95 1.15] 0.339 0.997."""
    assert run() == "[1.95 1.15] 0.339 0.997\n"


def test_matches_lstsq_and_the_residual_is_perpendicular():
    """The coefficients match np.linalg.lstsq, and A.T @ residual is zero."""
    least_squares = function("least_squares")
    coef, length = least_squares(A, NOISY)
    assert np.allclose(coef, np.linalg.lstsq(A, NOISY)[0])
    residual = NOISY - A @ coef
    assert np.allclose(A.T @ residual, 0)
    assert abs(length - np.linalg.norm(residual)) < 1e-9


def test_r_squared():
    """R squared is 1 for data on the line, and about 0.997 for the noisy data."""
    r_squared = function("r_squared")
    assert abs(r_squared(A, EXACT) - 1.0) < 1e-9
    assert abs(r_squared(A, NOISY) - 0.997) < 0.001
