import numpy as np

from checks import function, run

EXPECTED = 'column sums after centering: [0. 0. 0.]\nscores: [-11.25  -6.75  -2.25   2.25   6.75  11.25]\n'


def test_the_output():
    """Prints zero column sums and the six scores."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_shapes():
    """center zeroes the column sums of a 3 by 2 matrix, and score weights a 2 by 4 matrix row by row."""
    center = function("center")
    score = function("score")
    assert np.allclose(center(np.array([[1.0, 10.0], [2.0, 40.0], [6.0, 10.0]])).sum(axis=0), 0)
    assert np.allclose(score(np.ones((2, 4)), np.arange(4, dtype=np.float64)), [6.0, 6.0])
