import numpy as np

from checks import function, run


def test_the_output():
    """Prints [ 5.  3. -2.]."""
    assert run() == "[ 5.  3. -2.]\n"


def test_another_system():
    """Solves a 2-by-2 system too."""
    solve_system = function("solve_system")
    assert solve_system(np.array([[2.0, 1.0], [1.0, -1.0]]), np.array([5.0, 1.0])).tolist() == [2.0, 1.0]
