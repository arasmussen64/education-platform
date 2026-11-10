import numpy as np

from checks import function, run


def test_the_output():
    """Prints the loss and the first four entries of dz2."""
    printed = run()
    assert printed == '0.598\n[0.0354 0.0326 0.02   0.0082]\n', f"Your program printed:\n{printed}"


def test_known_losses():
    """Guessing a half costs log 2, and a prediction of exactly 1 for a true 0 stays finite."""
    loss = function("loss")
    assert abs(loss(np.full(16, 0.5), np.zeros(16)) - np.log(2)) < 1e-9
    assert np.isfinite(loss(np.array([1.0]), np.array([0.0])))
