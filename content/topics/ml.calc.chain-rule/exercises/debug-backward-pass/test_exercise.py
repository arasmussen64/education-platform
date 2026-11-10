import numpy as np

from checks import function, run

EXPECTED = 'y 0.854038\ndy/dx 0.388715\nmatches True\n'


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def test_the_output():
    """Prints y, dy/dx and matches True."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_at_another_point():
    """At x = -1 the derivative matches a central difference of y."""
    y = function("y")
    dy = function("dy")
    numeric = (y(-1 + 1e-6) - y(-1 - 1e-6)) / 2e-6
    assert abs(dy(-1.0) - numeric) < 1e-6
