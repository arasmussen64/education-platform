import numpy as np

from checks import function, run

EXPECTED = "[ 2.  3. -1.]\n"


def test_the_output():
    """Prints [ 2.  3. -1.]."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_another_system():
    """Agrees with np.linalg.solve on another 3-by-3 system."""
    gaussian_solve = function("gaussian_solve")
    A = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 3.0], [4.0, 0.0, 1.0]])
    b = np.array([5.0, 10.0, 9.0])
    assert np.allclose(gaussian_solve(A, b), np.linalg.solve(A, b))
