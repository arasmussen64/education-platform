import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def grad_round(p):
    return 2 * p


def grad_valley(p):
    return np.array([2 * p[0], 200 * p[1]])


def test_the_output():
    """Prints the three losses and Adam's first point."""
    assert run() == "plain 13.398\nmomentum 0.0009\nadam 0.0029\nadam's first step [9.7 0.7]\n"


def test_momentum_with_beta_zero_is_plain_descent():
    """With beta 0, each step halves the point on x² + y² at rate 0.25; with beta 0.5 the second step is longer."""
    momentum = function("momentum")
    path = momentum(grad_round, np.array([4.0, 2.0]), 0.25, 0.0, 3)
    assert len(path) == 3
    assert np.allclose(path[-1], [0.5, 0.25])
    path_m = momentum(grad_round, np.array([2.0, 0.0]), 0.1, 0.5, 2)
    assert np.allclose(path_m[0], [1.6, 0.0]) and np.allclose(path_m[1], [1.08, 0.0])


def test_momentum_beats_plain_on_the_valley():
    """After 100 steps at rate 0.005, momentum's loss is below plain descent's."""
    momentum = function("momentum")
    start = np.array([10.0, 1.0])
    plain = momentum(grad_valley, start, 0.005, 0.0, 100)[-1]
    fast = momentum(grad_valley, start, 0.005, 0.9, 100)[-1]
    assert grad_valley(fast) @ fast < grad_valley(plain) @ plain


def test_adams_first_step_and_its_arrival():
    """Adam's first step is exactly the rate against the gradient's sign, from any start; after 300 steps at rate 0.05 on x² + y² it is within 0.01 of the origin."""
    adam = function("adam")
    first = adam(grad_valley, np.array([-7.0, 0.002]), 0.25, 1)[0]
    assert np.allclose(first, [-6.75, -0.248], atol=1e-6)
    end = adam(grad_round, np.array([3.0, -4.0]), 0.05, 300)[-1]
    assert np.linalg.norm(end) < 0.01
