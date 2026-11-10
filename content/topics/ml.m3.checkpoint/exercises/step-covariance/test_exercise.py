import numpy as np

from checks import function, run


def test_the_output():
    """Prints the 3-by-3 covariance matrix."""
    printed = run()
    assert printed == "[[ 1.367  0.567  2.167]\n [ 0.567  1.367 -0.273]\n [ 2.167 -0.273  4.656]]\n", (
        f"Your program printed:\n{printed}"
    )


def test_matches_np_cov():
    """Agrees with np.cov on other points."""
    covariance = function("covariance")
    other = np.array([[1.0, 2.0, 0.0], [3.0, 1.0, 4.0], [2.0, 5.0, 1.0], [0.0, 2.0, 2.0]])
    assert np.allclose(covariance(other), np.cov(other, rowvar=False))
