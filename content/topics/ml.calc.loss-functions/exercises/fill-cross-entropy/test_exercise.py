import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three losses."""
    printed = run()
    assert printed == '0.992\n0.0\n27.631\n', f"Your program printed:\n{printed}"


def test_known_values():
    """Guessing a half for everything costs log 2; a 0.9 for a true 0 costs -log(0.1)."""
    cross_entropy = function("cross_entropy")
    assert abs(cross_entropy(np.array([0.5, 0.5, 0.5]), np.array([1.0, 0.0, 1.0])) - np.log(2)) < 1e-9
    assert abs(cross_entropy(np.array([0.9]), np.array([0.0])) + np.log(0.1)) < 1e-9
