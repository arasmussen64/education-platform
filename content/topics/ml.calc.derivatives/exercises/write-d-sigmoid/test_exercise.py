import numpy as np

from checks import function, run


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def test_the_output():
    """Prints the derivative at -4, 0 and 4, rounded to 4 places."""
    printed = run()
    assert printed == '[0.0177 0.25   0.0177]\n', f"Your program printed:\n{printed}"


def test_matches_a_numeric_slope():
    """At -3, -1, 0.5 and 2 the rule agrees with a central difference to six decimals."""
    d_sigmoid = function("d_sigmoid")
    for x in [-3.0, -1.0, 0.5, 2.0]:
        numeric = (sigmoid(x + 1e-6) - sigmoid(x - 1e-6)) / 2e-6
        assert abs(d_sigmoid(x) - numeric) < 1e-6


def test_arrays():
    """An array in gives an array of the same shape out, with 0.25 at zero."""
    d_sigmoid = function("d_sigmoid")
    result = d_sigmoid(np.array([[0.0, 1.0], [-1.0, 10.0]]))
    assert result.shape == (2, 2)
    assert abs(result[0, 0] - 0.25) < 1e-9
    assert result[1, 1] < 0.0001
