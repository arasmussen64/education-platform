import numpy as np

from checks import function, run

EXPECTED = 'x**2 at 3: 6.0\nsigmoid at 0: 0.25 0.25\nsigmoid at 2: 0.104994 0.104994\n'


def test_the_output():
    """Prints the three checked lines."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_slope_is_accurate():
    """slope gets x ** 3 at 2 right to six decimals."""
    slope = function("slope")
    assert abs(slope(lambda x: x**3, 2.0) - 12.0) < 1e-6


def test_the_rule_on_an_array():
    """d_sigmoid is the same at 1 and -1 (the curve is symmetric), and 0.25 at 0."""
    d_sigmoid = function("d_sigmoid")
    values = d_sigmoid(np.array([1.0, -1.0, 0.0]))
    assert abs(values[0] - values[1]) < 1e-12
    assert abs(values[2] - 0.25) < 1e-12
