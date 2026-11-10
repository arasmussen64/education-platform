import numpy as np

from checks import function, run


def test_the_output():
    """Prints the output shape, the parameter shapes and the count, then True."""
    printed = run()
    assert printed == '(6, 2) [(4, 8), (8,), (8, 2), (2,)] 58\nTrue\n', f"Your program printed:\n{printed}"


def test_other_stacks():
    """A one-layer stack is that layer; a three-layer stack runs all three in order and lists six parameters."""
    Sequential = function("Sequential")
    Dense = function("Dense")
    ReLU = function("ReLU")
    layer = Dense(3, 2, seed=9)
    X = np.array([[1.0, -1.0, 2.0], [0.5, 0.5, 0.5]])
    assert np.allclose(Sequential([layer]).forward(X), layer.forward(X))
    stack = Sequential([Dense(3, 4, seed=1), ReLU(), Dense(4, 4, seed=2), ReLU(), Dense(4, 1, seed=3)])
    by_hand = X
    for piece in stack.layers:
        by_hand = piece.forward(by_hand)
    assert np.allclose(stack.forward(X), by_hand) and stack.forward(X).shape == (2, 1)
    assert [p.shape for p in stack.parameters()] == [(3, 4), (4,), (4, 4), (4,), (4, 1), (1,)]
