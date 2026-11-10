import numpy as np

from checks import function, run

EXPECTED = 'mse 0.1375\ncross-entropy 0.992\n'


def test_the_output():
    """Prints the two losses."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_known_values():
    """Misses of 2 cost 4 under mse; a half costs log 2 under cross-entropy."""
    mse = function("mse")
    cross_entropy = function("cross_entropy")
    assert abs(mse(np.array([3.0, 3.0]), np.array([1.0, 1.0])) - 4.0) < 1e-12
    assert abs(cross_entropy(np.array([0.5]), np.array([1.0])) - np.log(2)) < 1e-9
