import numpy as np

from checks import function, run


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def test_the_output():
    """Prints the two derivatives and True."""
    printed = run()
    assert printed == '0.013296\n-0.25\nTrue\n', f"Your program printed:\n{printed}"


def test_other_units():
    """For a = 3, b = -1 at x = 0.4 the result matches a central difference, and a = 0 gives 0."""
    d = function("d_sigmoid_of_linear")
    numeric = (sigmoid(3 * 0.4 - 1 + 3e-6) - sigmoid(3 * 0.4 - 1 - 3e-6)) / 2e-6
    assert abs(d(3, -1, 0.4) - numeric) < 1e-6
    assert abs(d(0, 2, 1.0)) < 1e-12
