import numpy as np

from checks import function, run


def test_the_output():
    """Prints the forward and backward outputs."""
    assert run() == '[[2.0, 0.0, 0.0], [0.0, 3.0, 1.0]]\n[[1.0, 0.0, 0.0], [0.0, -2.0, 4.0]]\n'


def test_the_mask_comes_from_the_input():
    """The gradient passes where the input was positive, whatever the gradient's own sign."""
    ReLU = function("ReLU")
    relu = ReLU()
    relu.forward(np.array([[1.0, -1.0, 0.0]]))
    assert relu.backward(np.array([[-5.0, 5.0, 5.0]])).tolist() == [[-5.0, 0.0, 0.0]]
