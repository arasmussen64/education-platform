import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def numeric_gradient(f, p, h=1e-6):
    grad = np.zeros(len(p))
    for i in range(len(p)):
        step = np.zeros(len(p))
        step[i] = h
        grad[i] = (f(p + step) - f(p - step)) / (2 * h)
    return grad


def test_the_output():
    """Prints the four lines."""
    assert run() == 'mse 0.1375\nd_mse [-0.25  0.25  0.05 -0.1 ]\ncross-entropy 0.992\nd/dz [-0.04   0.167 -0.244]\n'


def test_mse_and_its_gradient():
    """mse is 0 for a perfect prediction and 1 for misses of 1; d_mse matches a numeric gradient."""
    mse = function("mse")
    d_mse = function("d_mse")
    target = np.array([1.0, 2.0, 3.0])
    assert mse(target, target) == 0
    assert abs(mse(target + 1, target) - 1.0) < 1e-12
    pred = np.array([0.5, 2.5, 2.0])
    assert np.abs(d_mse(pred, target) - numeric_gradient(lambda q: mse(q, target), pred)).max() < 1e-6


def test_cross_entropy_values():
    """Guessing a half costs log 2; perfect predictions cost about 0; a prediction of exactly 0 stays finite."""
    cross_entropy = function("cross_entropy")
    assert abs(cross_entropy(np.array([0.5, 0.5]), np.array([1.0, 0.0])) - np.log(2)) < 1e-9
    assert cross_entropy(np.array([1.0, 0.0]), np.array([1.0, 0.0])) < 1e-9
    assert np.isfinite(cross_entropy(np.array([0.0]), np.array([1.0])))


def test_gradient_through_the_sigmoid():
    """d_cross_entropy_dz matches a numeric gradient of cross_entropy(sigmoid(z), y)."""
    cross_entropy = function("cross_entropy")
    d = function("d_cross_entropy_dz")
    z = np.array([1.5, -0.5, 0.0, 3.0])
    y = np.array([0.0, 1.0, 1.0, 0.0])
    numeric = numeric_gradient(lambda q: cross_entropy(1 / (1 + np.exp(-q)), y), z)
    assert np.abs(d(z, y) - numeric).max() < 1e-6
