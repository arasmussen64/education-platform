import numpy as np

from checks import function, run

EXPECTED = 'gradient [2. 6.]\neast 2.0\nnorth-east 5.657\n'


def test_the_output():
    """Prints the gradient and the two rates."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_three_coordinates():
    """numeric_gradient gives [6, 3, 2] for f = x y z at (1, 2, 3)."""
    numeric_gradient = function("numeric_gradient")
    g = numeric_gradient(lambda p: p[0] * p[1] * p[2], np.array([1.0, 2.0, 3.0]))
    assert np.abs(g - [6.0, 3.0, 2.0]).max() < 1e-6


def test_direction_length_does_not_matter():
    """The rate along [0, 5] equals the rate along [0, 1]."""
    directional_derivative = function("directional_derivative")
    g = np.array([2.0, 6.0])
    assert abs(directional_derivative(g, np.array([0.0, 5.0])) - 6.0) < 1e-9
