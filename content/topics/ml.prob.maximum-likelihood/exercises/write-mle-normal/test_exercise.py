import numpy as np

from checks import function, run


def test_the_output():
    """Prints the fit, the two checks and the small sample's fit."""
    printed = run()
    assert printed == '169.87 9.89\nTrue True\n(5.0, 2.0)\n', f"Your program printed:\n{printed}"


def test_divides_by_n():
    """For [1, 3] the spread is 1 (dividing by n), not root 2."""
    mle_normal = function("mle_normal")
    mu, sigma = mle_normal(np.array([1.0, 3.0]))
    assert mu == 2.0 and abs(sigma - 1.0) < 1e-12
