import numpy as np

from checks import function, run


def test_the_output():
    """The gradient check passes and the counts are right."""
    printed = run()
    assert printed == 'gradient check: passes\n75 (6, 3)\n', f"Your program printed:\n{printed}"


def test_by_hand():
    """One dense layer's three gradients on a tiny case, by hand."""
    Dense = function("Dense")
    layer = Dense(2, 2, seed=0)
    layer.W[:] = np.array([[1.0, 2.0], [3.0, 4.0]])
    layer.forward(np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]))
    grad_in = layer.backward(np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]))
    assert layer.dW.tolist() == [[2.0, 1.0], [1.0, 2.0]] and layer.db.tolist() == [2.0, 2.0]
    assert grad_in.tolist() == [[1.0, 3.0], [2.0, 4.0], [3.0, 7.0]]
