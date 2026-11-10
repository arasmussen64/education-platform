import numpy as np

from checks import function, run


def test_these_pairs():
    """Prints 45.0, then 90.0."""
    printed = run()
    assert printed == "45.0\n90.0\n", f"Your program printed:\n{printed}"


def test_other_pairs():
    """Opposite vectors give 180, and a vector with a scaled copy of itself gives 0."""
    angle_degrees = function("angle_degrees")
    assert angle_degrees(np.array([1.0, 0.0]), np.array([-2.0, 0.0])) == 180.0
    assert angle_degrees(np.array([1.0, 2.0]), np.array([2.0, 4.0])) == 0.0
