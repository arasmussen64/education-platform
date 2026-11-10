import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

X = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [2.0, 3.0]])
A_EXACT = np.column_stack([X, np.ones(4)])
Z_EXACT = np.array([3.0, 5.0, 2.0, 4.0])


def test_the_output():
    """Prints the plane, the lstsq check and three losses."""
    assert run() == 'plane [ 2.015 -1.035  3.024]\nlstsq agrees True\nloss 21.2408 0.7298 0.0063\n'


def test_exact_plane():
    """Four points on z = 2x - y + 3: descent finds [2, -1, 3] to three decimals and the loss falls below 1e-6."""
    fit_by_descent = function("fit_by_descent")
    w, losses = fit_by_descent(A_EXACT, Z_EXACT, 0.1, 4000)
    assert np.allclose(w, [2.0, -1.0, 3.0], atol=1e-3)
    assert losses[-1] < 1e-6


def test_losses_start_at_zero_weights_and_never_rise():
    """losses[0] is the loss at all-zero weights (the mean of z squared), there is one entry per step, and the curve never rises."""
    fit_by_descent = function("fit_by_descent")
    w, losses = fit_by_descent(A_EXACT, Z_EXACT, 0.1, 300)
    assert len(losses) == 300
    assert abs(losses[0] - np.mean(Z_EXACT**2)) < 1e-9
    assert all(b <= a + 1e-12 for a, b in zip(losses, losses[1:]))


def test_gradient_matches_a_numeric_one():
    """gradient(A, w, z) agrees with a one-coordinate-at-a-time numeric gradient of mse."""
    mse = function("mse")
    gradient = function("gradient")
    w = np.array([0.5, -0.5, 1.0])
    numeric = np.zeros(3)
    for i in range(3):
        step = np.zeros(3)
        step[i] = 1e-6
        numeric[i] = (mse(A_EXACT, w + step, Z_EXACT) - mse(A_EXACT, w - step, Z_EXACT)) / 2e-6
    assert np.abs(gradient(A_EXACT, w, Z_EXACT) - numeric).max() < 1e-6
