import numpy as np

from checks import function, run


def test_the_output():
    """Prints the unit direction, then rates of 3, 0 and 5."""
    printed = run()
    assert printed == '[0.6 0.8]\n3.0\n0.0\n5.0\n', f"Your program printed:\n{printed}"


def test_other_gradients():
    """Unit length for another gradient; the rate along a direction of length 10 is the same as along length 1."""
    steepest_ascent = function("steepest_ascent")
    directional_derivative = function("directional_derivative")
    g = np.array([1.0, 2.0, 2.0])
    assert np.allclose(steepest_ascent(g), [1 / 3, 2 / 3, 2 / 3])
    assert abs(directional_derivative(g, np.array([0.0, 10.0, 0.0])) - 2.0) < 1e-9
    assert abs(directional_derivative(g, np.array([0.0, 1.0, 0.0])) - 2.0) < 1e-9
    assert abs(directional_derivative(g, np.array([2.0, -1.0, 0.0]))) < 1e-9
