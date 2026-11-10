import numpy as np

from checks import function, run


def test_the_output():
    """Prints [0.924]."""
    assert run() == '[0.924]\n'


def test_two_examples_and_the_bend():
    """Two examples give two probabilities, and a negative hidden score is bent to zero before the output."""
    forward = function("forward")
    X = np.array([[1.0, 2.0], [-3.0, 0.0]])
    W1 = np.array([[1.0, -1.0], [0.0, 1.0]])
    b1 = np.array([0.0, -1.0])
    W2 = np.array([2.0, -1.0])
    p = forward(X, W1, b1, W2, 0.5)
    assert p.shape == (2,)
    assert abs(p[1] - 1 / (1 + np.exp(1.5))) < 1e-9
