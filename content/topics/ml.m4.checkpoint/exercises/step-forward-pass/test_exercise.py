import numpy as np

from checks import function, run


def test_the_output():
    """Prints the shapes and the first four probabilities."""
    printed = run()
    assert printed == '(16, 4) (16, 4) (16,)\n[0.566 0.521 0.32  0.131]\n', f"Your program printed:\n{printed}"


def test_the_bend():
    """A hidden score below zero comes out of the bend as exactly zero."""
    forward = function("forward")
    params = {"W1": np.array([[1.0, -1.0], [0.0, 0.0]]), "b1": np.zeros(2), "W2": np.ones(2), "b2": np.array(0.0)}
    z1, h, p = forward(np.array([[2.0, 0.0]]), params)
    assert z1.tolist() == [[2.0, -2.0]] and h.tolist() == [[2.0, 0.0]]
