import numpy as np

from checks import function, run


def test_this_system():
    """Prints 2.0 1.0."""
    printed = run()
    assert printed == "2.0 1.0\n", f"Your program printed:\n{printed}"


def test_another_system():
    """3x + y = 9 and x + 2y = 8 give x = 2, y = 3."""
    solve_2x2 = function("solve_2x2")
    x, y = solve_2x2(np.array([[3.0, 1.0, 9.0], [1.0, 2.0, 8.0]]))
    assert np.allclose([x, y], [2.0, 3.0])
