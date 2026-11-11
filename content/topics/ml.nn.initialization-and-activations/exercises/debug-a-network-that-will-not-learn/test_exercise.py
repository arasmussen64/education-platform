import numpy as np

from checks import function, run

EXPECTED = 'loss 1.1388 -> 0.0006 | the loss fell by more than half: True\nhidden units identical: False | dead hidden units: 0 of 8\n'


def test_the_output():
    """Prints a loss that fell by half, distinct hidden units and no dead ones."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_the_starting_layer():
    """A fresh Dense(3, 8) at He's scale has distinct columns, zero biases and a spread near sqrt(2 / 3)."""
    Dense = function("Dense")
    layer = Dense(3, 8, seed=4, scale=np.sqrt(2 / 3))
    assert not np.allclose(layer.W, layer.W[:, :1]) and np.array_equal(layer.b, np.zeros(8))
    assert 0.3 < layer.W.std() < 1.6
