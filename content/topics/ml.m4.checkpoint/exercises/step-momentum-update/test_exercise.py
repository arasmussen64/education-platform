import numpy as np

from checks import function, run


def test_the_output():
    """Prints the two losses and W2."""
    printed = run()
    assert printed == '0.598 0.014\n[-2.954 -3.403  3.826 -3.677]\n', f"Your program printed:\n{printed}"


def test_two_steps_follow_the_rule():
    """Two steps of train match two heavy-ball steps computed from the program's own backward pass."""
    forward = function("forward")
    backward = function("backward")
    train = function("train")
    g = np.array([-1.5, -0.5, 0.5, 1.5])
    X = np.array([[a, b] for a in g for b in g])
    y = (X[:, 0] ** 2 + X[:, 1] ** 2 < 1).astype(float)

    def fresh():
        return {
        "W1": np.array([[-0.5, -0.1, 1.3, 0.5], [-1.3, 0.2, -0.5, 0.1]]),
        "b1": np.array([-0.5, 0.1, 0.15, 0.5]),
        "W2": np.array([0.3, 0.4, -1.2, 1.8]),
        "b2": np.array(0.2),
    }

    expected = fresh()
    vel = {key: np.zeros_like(value) for key, value in expected.items()}
    for step in range(2):
        z1, h, p = forward(X, expected)
        grads = backward(X, y, expected, z1, h, p)
        for key in expected:
            vel[key] = 0.9 * vel[key] + grads[key]
            expected[key] = expected[key] - 0.1 * vel[key]
    params = fresh()
    train(X, y, params, 0.1, 0.9, 2)
    for key in params:
        assert np.allclose(params[key], expected[key]), key
