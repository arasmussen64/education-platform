import numpy as np

from checks import function, run


def test_the_output():
    """Prints the shape, the zero biases and the two spreads."""
    assert run() == '(100, 50) True 0.14\n0.1\n'


def test_the_rule():
    """ReLU gets sqrt(2) times the tanh scale, the biases are zero, and the same seed gives the same weights."""
    start_weights = function("start_weights")
    W_relu, b = start_weights(64, 32, "relu", seed=2)
    W_tanh, _ = start_weights(64, 32, "tanh", seed=2)
    assert np.array_equal(b, np.zeros(32)) and np.allclose(W_relu, W_tanh * 2 ** 0.5)
    assert np.array_equal(W_relu, start_weights(64, 32, "relu", seed=2)[0])
