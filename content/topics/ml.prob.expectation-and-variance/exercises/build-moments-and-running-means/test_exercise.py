import math

import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the die, the ten dice, the running means and the z-scores."""
    assert run() == 'one die 3.5 2.9167\nten dice 35.0 29.1667\nrunning [3.    3.61  3.51  3.498]\nz [-1.  2.]\n'


def test_moments_of_known_tables():
    """A Bernoulli(0.3) has moments (0.3, 0.21); a binomial(10, 0.3) table has (3, 2.1)."""
    moments = function("moments")
    mean, variance = moments(np.array([0.0, 1.0]), np.array([0.7, 0.3]))
    assert abs(mean - 0.3) < 1e-12 and abs(variance - 0.21) < 1e-12
    ks = np.arange(11)
    probs = np.array([math.comb(10, k) * 0.3**k * 0.7 ** (10 - k) for k in ks])
    mean, variance = moments(ks, probs)
    assert abs(mean - 3.0) < 1e-9 and abs(variance - 2.1) < 1e-9


def test_sum_of_independent():
    """Means add and variances add, not standard deviations: three variables with variance 4 give variance 12."""
    sum_of_independent = function("sum_of_independent")
    assert sum_of_independent([1.0, 2.0, 3.0], [4.0, 4.0, 4.0]) == (6.0, 12.0)


def test_running_means():
    """The running means of [2, 4, 6] are [2, 3, 4]."""
    running_means = function("running_means")
    assert running_means(np.array([2.0, 4.0, 6.0])).tolist() == [2.0, 3.0, 4.0]


def test_standardize():
    """The mean standardizes to 0 and one spread above to 1."""
    standardize = function("standardize")
    assert standardize(50, 50, 5) == 0 and standardize(55, 50, 5) == 1
