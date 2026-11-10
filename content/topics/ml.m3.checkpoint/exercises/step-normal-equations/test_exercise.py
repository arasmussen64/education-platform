import numpy as np

from checks import function, run


def test_the_output():
    """Prints the plane's coefficients."""
    printed = run()
    assert printed == "plane [ 2.015 -1.035  3.024]\n", f"Your program printed:\n{printed}"


def test_exact_plane():
    """Points exactly on z = 2x - y + 3 give [2, -1, 3]."""
    fit_plane = function("fit_plane")
    assert np.allclose(fit_plane(np.array([[0.0, 0.0, 3.0], [1.0, 0.0, 5.0], [0.0, 1.0, 2.0], [2.0, 3.0, 4.0], [3.0, 1.0, 8.0], [1.0, 2.0, 3.0]])), [2.0, -1.0, 3.0])
