import numpy as np

from checks import function, run


def test_the_output():
    """Prints dW2, dW1 and True."""
    printed = run()
    assert printed == '[-0.141 -0.139 -0.055 -0.094]\n[[ 0.079  0.023  0.084  0.   ]\n [ 0.063  0.018  0.    -0.087]]\nTrue\n', f"Your program printed:\n{printed}"


def test_shapes_and_the_mask():
    """Gradients have their parameters' shapes, and a hidden unit that is off for every example gets a zero gradient."""
    backward = function("backward")
    X = np.array([[1.0, 0.0], [0.0, 1.0]])
    y = np.array([1.0, 0.0])
    W2 = np.array([0.5, -0.5, 1.0])
    z1 = np.array([[1.0, -1.0, 2.0], [0.5, -2.0, 1.0]])
    h = np.maximum(z1, 0.0)
    p = np.array([0.7, 0.4])
    dW1, db1, dW2, db2 = backward(X, y, W2, z1, h, p)
    assert dW1.shape == (2, 3) and db1.shape == (3,) and dW2.shape == (3,)
    assert np.abs(dW1[:, 1]).max() == 0 and db1[1] == 0
