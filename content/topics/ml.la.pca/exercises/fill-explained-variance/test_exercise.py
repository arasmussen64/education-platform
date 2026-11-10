import numpy as np

from checks import function, run


def test_the_output():
    """Prints [0.984 0.016], then [1. 0.]."""
    printed = run()
    assert printed == "[0.984 0.016]\n[1. 0.]\n", f"Your program printed:\n{printed}"


def test_three_features():
    """Data that varies along one axis only puts all the variance in one component."""
    explained = function("explained")
    X = np.array([[1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [3.0, 0.0, 0.0], [4.0, 0.0, 0.0]])
    assert explained(X).tolist() == [1.0, 0.0, 0.0]
