import numpy as np

from checks import function, run

EXPECTED = 'output shape: (2, 2)\nhidden values are never negative: True | some are zero: True\n'


def test_the_output():
    """Prints the output shape and the two facts about the hidden layer."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_classes():
    """Dense builds W as (inputs, outputs) and computes X @ W + b; ReLU zeroes negatives and keeps positives."""
    Dense = function("Dense")
    ReLU = function("ReLU")
    layer = Dense(5, 2, seed=3)
    assert layer.W.shape == (5, 2) and layer.b.shape == (2,)
    X = np.random.default_rng(0).standard_normal((3, 5))
    assert np.allclose(layer.forward(X), X @ layer.W + layer.b)
    assert ReLU().forward(np.array([-1.0, 0.0, 2.0])).tolist() == [0.0, 0.0, 2.0]
