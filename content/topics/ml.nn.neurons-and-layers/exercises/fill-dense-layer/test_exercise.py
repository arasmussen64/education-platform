import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three rows and the parameter shapes."""
    printed = run()
    assert printed == '[[0.1, -0.3, 0.5], [0.1, -0.3, -0.5], [-0.65, 1.2, -0.3]]\n[(2, 3), (3,)] 9\n', f"Your program printed:\n{printed}"


def test_another_layer():
    """A layer with a single neuron gives the weighted sum plus the bias for every row, and its parameters are W and b."""
    Dense = function("Dense")
    layer = Dense(np.array([[2.0], [-1.0]]), np.array([0.5]))
    assert layer.forward(np.array([[1.0, 1.0], [3.0, 0.0]])).tolist() == [[1.5], [6.5]]
    W, b = layer.parameters()
    assert W.shape == (2, 1) and b.shape == (1,)
