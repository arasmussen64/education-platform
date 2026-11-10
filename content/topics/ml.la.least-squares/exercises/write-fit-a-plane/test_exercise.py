import numpy as np

from checks import function, run


def test_the_output():
    """Prints [ 2. -1.  3.]."""
    printed = run()
    assert printed == "[ 2. -1.  3.]\n", f"Your program printed:\n{printed}"


def test_another_plane():
    """Recovers z = 0.5x + 4y - 1 from five points on it."""
    fit_plane = function("fit_plane")
    X = np.array([[1.0, 1.0], [2.0, 0.0], [0.0, 3.0], [1.0, 2.0], [3.0, 1.0]])
    z = 0.5 * X[:, 0] + 4 * X[:, 1] - 1
    assert np.allclose(fit_plane(X, z), [0.5, 4.0, -1.0])
