import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

g = np.array([-1.5, -0.5, 0.5, 1.5])
X = np.array([[a, b] for a in g for b in g])
y = (np.abs(X[:, 0] + X[:, 1]) < 1).astype(float)


def start_params():
    return {
        "W1": np.array([[0.2, -0.4, -0.3, -2.0], [1.4, 0.9, -0.3, 0.6]]),
        "b1": np.array([0.1, -0.2, 0.25, -0.15]),
        "W2": np.array([-0.3, -0.6, 0.4, -0.1]),
        "b2": np.array(0.0),
    }


def other_params():
    return {
        "W1": np.array([[-0.5, -0.1, 1.3, 0.5], [-1.3, 0.2, -0.5, 0.1]]),
        "b1": np.array([-0.5, 0.1, 0.15, 0.5]),
        "W2": np.array([0.3, 0.4, -1.2, 1.8]),
        "b2": np.array(0.2),
    }


def central(f, W, h=1e-6):
    grad = np.zeros_like(W)
    for index in np.ndindex(W.shape):
        step = np.zeros_like(W)
        step[index] = h
        grad[index] = (f(W + step) - f(W - step)) / (2 * h)
    return grad


def test_the_output():
    """Prints the loss curve, the accuracy and the classes."""
    assert run() == 'loss 0.702 0.004 0.001\naccuracy 1.0\nclasses [0 0 0 1 0 0 1 0 0 1 0 0 1 0 0 0]\n'


def test_forward_and_loss():
    """forward gives the right shapes with a non-negative hidden layer, and loss is log 2 for guessing a half."""
    forward = function("forward")
    loss = function("loss")
    z1, h, p = forward(X, other_params())
    assert z1.shape == (16, 4) and h.shape == (16, 4) and p.shape == (16,)
    assert (h >= 0).all() and ((p > 0) & (p < 1)).all()
    assert abs(loss(np.full(16, 0.5), y) - np.log(2)) < 1e-9


def test_every_gradient_from_other_weights():
    """From other starting weights, every gradient matches a numeric one."""
    forward = function("forward")
    loss = function("loss")
    backward = function("backward")
    params = other_params()
    z1, h, p = forward(X, params)
    grads = backward(X, y, params, z1, h, p)
    for key in params:
        numeric = central(lambda value, key=key: loss(forward(X, {**params, key: value})[2], y), params[key])
        assert np.allclose(grads[key], numeric, atol=1e-6), key


def test_the_momentum_update():
    """Two steps of train match two heavy-ball steps computed from the program's own backward pass."""
    forward = function("forward")
    backward = function("backward")
    train = function("train")
    expected = other_params()
    vel = {key: np.zeros_like(value) for key, value in expected.items()}
    for step in range(2):
        z1, h, p = forward(X, expected)
        grads = backward(X, y, expected, z1, h, p)
        for key in expected:
            vel[key] = 0.9 * vel[key] + grads[key]
            expected[key] = expected[key] - 0.1 * vel[key]
    params = other_params()
    losses = train(X, y, params, 0.1, 0.9, 2)
    assert len(losses) == 2
    for key in params:
        assert np.allclose(params[key], expected[key]), key


def test_training_learns_the_data():
    """From the starting weights, 2000 steps give every class right and a loss below 0.05, with one loss per step."""
    forward = function("forward")
    train = function("train")
    params = start_params()
    losses = train(X, y, params, 0.1, 0.9, 2000)
    assert len(losses) == 2000
    assert losses[-1] < 0.05 < losses[0]
    p = forward(X, params)[2]
    assert ((p > 0.5) == (y == 1)).all()
