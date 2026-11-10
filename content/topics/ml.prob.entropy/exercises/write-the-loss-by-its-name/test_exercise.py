import numpy as np

from checks import function, run


def test_the_output():
    """Prints the loss twice, then the near-perfect and the guessing losses."""
    printed = run()
    assert printed == '0.299\n0.299\n0.0005 0.6931\n', f"Your program printed:\n{printed}"


def test_matches_the_formula():
    """On other labels and probabilities the result equals Module 4's formula."""
    cross_entropy_loss = function("cross_entropy_loss")
    y = np.array([0.0, 1.0, 1.0, 0.0, 1.0])
    p = np.array([0.1, 0.8, 0.55, 0.3, 0.95])
    expected = -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
    assert abs(cross_entropy_loss(y, p) - expected) < 1e-12
