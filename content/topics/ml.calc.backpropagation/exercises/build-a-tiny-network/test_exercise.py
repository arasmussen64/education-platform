import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
Y = np.array([0.0, 1.0, 1.0, 0.0])


def other_params():
    return {
        "W1": np.array([[0.2, -0.5, -0.4, -2.4], [1.8, 1.1, -0.3, 0.8]]),
        "b1": np.array([0.1, -0.3, 0.5, -0.2]),
        "W2": np.array([-0.3, -0.8, 0.5, -0.1]),
        "b2": np.array(0.4),
    }


def start_params():
    return {
        "W1": np.array([[0.3, 0.8, 0.3, -1.3], [0.9, 0.4, -0.5, 0.6]]),
        "b1": np.array([0.2, 0.1, 0.1, 0.3]),
        "W2": np.array([-0.7, -0.2, -0.5, 0.6]),
        "b2": np.array(0.0),
    }


def central(f, W, h=1e-6):
    grad = np.zeros_like(W)
    for index in np.ndindex(W.shape):
        step = np.zeros_like(W)
        step[index] = h
        grad[index] = (f(W + step) - f(W - step)) / (2 * h)
    return grad


def test_the_output():
    """Prints four checks, the loss curve, the predictions and the accuracy."""
    assert run() == 'check W1 True\ncheck b1 True\ncheck W2 True\ncheck b2 True\nloss 0.732 0.081 0.004 0.001\npredictions [0. 1. 1. 0.]\naccuracy 1.0\n'


def test_forward_and_loss():
    """forward gives the right shapes and a loss of about log 2 for a network that guesses a half."""
    forward = function("forward")
    loss = function("loss")
    params = other_params()
    z1, h, p = forward(X, params)
    assert z1.shape == (4, 4) and h.shape == (4, 4) and p.shape == (4,)
    assert (h >= 0).all()
    assert abs(loss(np.array([0.5, 0.5, 0.5, 0.5]), Y) - np.log(2)) < 1e-9


def test_every_gradient_from_other_weights():
    """From other starting weights, every gradient matches a numeric one."""
    forward = function("forward")
    loss = function("loss")
    backward = function("backward")
    params = other_params()
    z1, h, p = forward(X, params)
    grads = backward(X, Y, params, z1, h, p)
    for key in params:
        numeric = central(lambda value, key=key: loss(forward(X, {**params, key: value})[2], Y), params[key])
        assert np.allclose(grads[key], numeric, atol=1e-6), key


def test_training_learns_xor():
    """train returns one loss per step, the loss falls below 0.05, and all four predictions are right."""
    forward = function("forward")
    train = function("train")
    params = start_params()
    losses = train(X, Y, params, 0.5, 1000)
    assert len(losses) == 1000
    assert losses[-1] < 0.05 < losses[0]
    p = forward(X, params)[2]
    assert ((p > 0.5) == (Y == 1)).all()
