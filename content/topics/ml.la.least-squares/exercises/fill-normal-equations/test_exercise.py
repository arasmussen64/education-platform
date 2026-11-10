import numpy as np

from checks import function, run


def test_the_output():
    """Prints the exact fit, then the noisy fit."""
    printed = run()
    assert printed == "[2. 1.]\n[1.95 1.15]\n", f"Your program printed:\n{printed}"


def test_other_data():
    """Fits other points, and gives slope 0 for a flat line."""
    fit_line = function("fit_line")
    assert np.allclose(fit_line(np.array([0.0, 2.0, 4.0]), np.array([1.0, 2.0, 2.0])), [0.25, 7 / 6])
    assert np.allclose(fit_line(np.array([1.0, 2.0, 3.0]), np.array([2.0, 2.0, 2.0])), [0.0, 2.0])
