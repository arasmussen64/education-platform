import numpy as np

from checks import function, run


def test_the_output():
    """Prints [0.776 0.224 0.   ]."""
    printed = run()
    assert printed == "[0.776 0.224 0.   ]\n", f"Your program printed:\n{printed}"


def test_shares_sum_to_one_descending():
    """For other points the shares are the covariance's eigenvalues over their total, largest first."""
    shares = function("shares")
    other = np.array([[1.0, 2.0, 0.0], [3.0, 1.0, 4.0], [2.0, 5.0, 1.0], [0.0, 2.0, 2.0]])
    s = shares(other)
    values = np.linalg.eigvalsh(np.cov(other, rowvar=False))[::-1]
    assert np.allclose(s, values / values.sum())
    assert abs(s.sum() - 1) < 1e-9
