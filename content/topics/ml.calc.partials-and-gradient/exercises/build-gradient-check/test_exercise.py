import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the gradient, the check and the steepest direction."""
    assert run() == 'gradient [ 2.  3. 29.]\ngap below 1e-6 True\nsteepest [0.068 0.103 0.992]\n'


def test_numeric_gradient():
    """For f = x y² + exp(z) at (1, 2, 0) the estimate is [4, 4, 1] to six decimals, one coordinate at a time."""
    numeric_gradient = function("numeric_gradient")
    g = numeric_gradient(lambda p: p[0] * p[1] ** 2 + np.exp(p[2]), np.array([1.0, 2.0, 0.0]))
    assert np.abs(g - [4.0, 4.0, 1.0]).max() < 1e-6


def test_check_gradient_reports_the_largest_gap():
    """A formula that is right gives a gap below 1e-6; one that is off by 0.5 in one slot at one point gives 0.5."""
    check_gradient = function("check_gradient")

    def f(p):
        return p[0] ** 2 + p[1] ** 3

    def right(p):
        return np.array([2 * p[0], 3 * p[1] ** 2])

    def off(p):
        return right(p) + np.array([0.0, 0.5 * (p[0] == 1.0)])

    points = [np.array([1.0, 1.0]), np.array([2.0, -1.0])]
    assert check_gradient(f, right, points) < 1e-6
    assert abs(check_gradient(f, off, points) - 0.5) < 1e-5


def test_steepest():
    """steepest([3, 4]) is [0.6, 0.8], and the result always has length 1."""
    steepest = function("steepest")
    assert np.allclose(steepest(np.array([3.0, 4.0])), [0.6, 0.8])
    assert abs(np.linalg.norm(steepest(np.array([1.0, -2.0, 2.0]))) - 1.0) < 1e-9
