import numpy as np

from checks import function, run

EXPECTED = 'loss 0.598 0.006 0.001\naccuracy 1.0\nclasses [0 0 0 0 0 1 1 0 0 1 1 0 0 0 0 0]\n'


def test_the_output():
    """Prints the loss curve, the accuracy and the classes."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_mask_comes_before_dW1():
    """A hidden unit that is off for every example gets a zero gradient in W1 and b1, and dh has the hidden layer's shape."""
    backward = function("backward")
    params = {
        "W1": np.zeros((2, 3)),
        "b1": np.zeros(3),
        "W2": np.array([0.5, -0.5, 1.0]),
        "b2": np.array(0.0),
    }
    X = np.array([[1.0, 0.0], [0.0, 1.0]])
    y = np.array([1.0, 0.0])
    z1 = np.array([[1.0, -1.0, 2.0], [0.5, -2.0, 1.0]])
    h = np.maximum(z1, 0.0)
    p = np.array([0.7, 0.4])
    grads = backward(X, y, params, z1, h, p)
    assert grads["W1"].shape == (2, 3)
    assert np.abs(grads["W1"][:, 1]).max() == 0 and grads["b1"][1] == 0
    assert np.abs(grads["W1"][:, 0]).max() > 0


def test_descent_not_ascent():
    """After twenty steps the loss is lower than at the start."""
    forward = function("forward")
    loss = function("loss")
    train = function("train")
    g = np.array([-1.5, -0.5, 0.5, 1.5])
    X = np.array([[a, b] for a in g for b in g])
    y = (X[:, 0] ** 2 + X[:, 1] ** 2 < 1).astype(float)
    params = {
        "W1": np.array([[0.2, -0.4, -0.3, -2.0], [1.4, 0.9, -0.3, 0.6]]),
        "b1": np.array([0.1, -0.2, 0.25, -0.15]),
        "W2": np.array([-0.3, -0.6, 0.4, -0.1]),
        "b2": np.array(0.0),
    }
    losses = train(X, y, params, 0.1, 0.9, 20)
    assert loss(forward(X, params)[2], y) < losses[0]
