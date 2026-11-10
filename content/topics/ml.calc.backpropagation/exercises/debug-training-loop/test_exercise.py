import numpy as np

from checks import function, run

EXPECTED = 'start 0.732\nend 0.001\npredictions [0. 1. 1. 0.]\n'


def test_the_output():
    """Prints the starting loss, the final loss and the predictions."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_mask():
    """A hidden unit that is off for every example gets a zero gradient; dW1 has W1's shape."""
    backward = function("backward")
    X = np.array([[1.0, 0.0], [0.0, 1.0]])
    y = np.array([1.0, 0.0])
    W2 = np.array([0.5, -0.5, 1.0, 2.0])
    z1 = np.array([[1.0, -1.0, 2.0, 0.5], [0.5, -2.0, 1.0, 0.1]])
    h = np.maximum(z1, 0.0)
    p = np.array([0.7, 0.4])
    dW1, db1, dW2, db2 = backward(X, y, W2, z1, h, p)
    assert dW1.shape == (2, 4)
    assert np.abs(dW1[:, 1]).max() == 0
    assert np.abs(dW1[:, 0]).max() > 0
