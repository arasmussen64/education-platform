import numpy as np

from checks import function, printed, run

EXPECTED = "eigenvalue 2.0 check True\neigenvalue 3.0 check True\n"


def test_the_output():
    """Prints both eigenvalues with a passing check."""
    out = run()
    assert out == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{out}"


def test_a_wrong_pair_is_caught():
    """A wrong eigenvalue is reported as False, and a right one as True, in order."""
    report = function("report")
    A = np.array([[5.0, 0.0], [0.0, 1.0]])
    out = printed(report, A, np.array([5.0, 2.0]), np.eye(2))
    assert out == "eigenvalue 5.0 check True\neigenvalue 2.0 check False\n", f"It printed:\n{out}"
