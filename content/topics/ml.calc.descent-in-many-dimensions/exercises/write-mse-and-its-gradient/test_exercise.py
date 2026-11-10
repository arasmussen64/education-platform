import numpy as np

from checks import function, run


def test_the_output():
    """Prints the gradient at zero and two Trues."""
    printed = run()
    assert printed == '[-6.5 -7.  -7. ]\nTrue\nTrue\n', f"Your program printed:\n{printed}"


def test_at_the_solution():
    """At the exact plane [2, -1, 3] the error is 0 and the gradient is zero; at [2, -1, 4] the error is 1."""
    mse = function("mse")
    mse_gradient = function("mse_gradient")
    assert abs(mse(np.array([2.0, -1.0, 3.0]))) < 1e-12
    assert np.abs(mse_gradient(np.array([2.0, -1.0, 3.0]))).max() < 1e-12
    assert abs(mse(np.array([2.0, -1.0, 4.0])) - 1.0) < 1e-12
    assert np.allclose(mse_gradient(np.array([2.0, -1.0, 4.0])), [1.5, 2.0, 2.0])
