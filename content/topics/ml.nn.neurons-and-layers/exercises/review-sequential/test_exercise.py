import numpy as np

from checks import function, run


def test_the_output():
    """Prints the shape and the count."""
    assert run() == '(7, 1) 26\n'


def test_the_stack():
    """A [4, 3, 2] stack matches its layers called one by one and lists parameters of the right shapes."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    Sequential = function("Sequential")
    stack = Sequential([Dense(4, 3, seed=1), ReLU(), Dense(3, 2, seed=2)])
    X = np.random.default_rng(2).standard_normal((5, 4))
    by_hand = stack.layers[2].forward(stack.layers[1].forward(stack.layers[0].forward(X)))
    assert np.allclose(stack.forward(X), by_hand)
    assert [p.shape for p in stack.parameters()] == [(4, 3), (3,), (3, 2), (2,)]
