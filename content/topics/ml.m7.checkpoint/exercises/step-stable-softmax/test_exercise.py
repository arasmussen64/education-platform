import numpy as np

from checks import function, run


def test_the_output():
    """Prints two finite rows."""
    printed = run()
    assert printed == '[[0.269, 0.731], [0.269, 0.731]]\n', f"Your program printed:\n{printed}"


def test_extremes():
    """Logits of 5,000 and of -5,000 give finite rows that sum to 1."""
    softmax = function("softmax")
    P = softmax(np.array([[5000.0, 5001.0], [-5000.0, -5001.0]]))
    assert not np.isnan(P).any() and np.allclose(P.sum(axis=1), 1)
