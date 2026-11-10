import numpy as np

from checks import function, run


def test_the_output():
    """Prints the dead fraction and the two saturated fractions."""
    printed = run()
    assert printed == '0.5 0.5 0.75\n', f"Your program printed:\n{printed}"


def test_other_batches():
    """A unit that fires once is alive; all-zero outputs are all dead; saturation counts both signs and respects the threshold."""
    dead_fraction = function("dead_fraction")
    saturated_fraction = function("saturated_fraction")
    assert dead_fraction(np.array([[0.0, 0.0], [0.0, 0.1]])) == 0.5
    assert dead_fraction(np.zeros((5, 4))) == 1.0 and dead_fraction(np.ones((5, 4))) == 0.0
    Z = np.array([[-5.0, 5.0, 3.0, -3.0]])
    assert saturated_fraction(Z) == 0.5 and saturated_fraction(Z, threshold=2.0) == 1.0 and saturated_fraction(Z, threshold=6.0) == 0.0
