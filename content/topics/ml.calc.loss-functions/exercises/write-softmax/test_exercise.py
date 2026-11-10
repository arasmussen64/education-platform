import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three probabilities and [0.5 0.5]."""
    printed = run()
    assert printed == '[0.659 0.242 0.099]\n[0.5 0.5]\n', f"Your program printed:\n{printed}"


def test_properties():
    """Probabilities sum to 1, keep the scores' order, and survive scores of 5000."""
    softmax = function("softmax")
    p = softmax(np.array([3.0, -1.0, 0.5, 2.0]))
    assert abs(p.sum() - 1) < 1e-12
    assert list(np.argsort(p)) == list(np.argsort([3.0, -1.0, 0.5, 2.0]))
    big = softmax(np.array([5000.0, 4999.0]))
    assert np.isfinite(big).all()
    assert abs(big[0] - 1 / (1 + np.exp(-1))) < 1e-9
