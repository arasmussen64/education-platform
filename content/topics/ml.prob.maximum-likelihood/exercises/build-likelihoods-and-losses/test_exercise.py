import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the coin fits, the labels' likelihood two ways and three normal losses."""
    assert run() == 'coin 0.75 0.3\nlabels 1.196 1.196\nnormal [8.271, 7.16, 8.271]\n'


def test_coins():
    """The fitted bias is the fraction of heads, to the grid's resolution, for 1 in 4 and 99 in 100."""
    mle_coin = function("mle_coin")
    assert abs(mle_coin(1, 4) - 0.25) < 0.001
    assert abs(mle_coin(99, 100) - 0.99) < 0.001


def test_nll_bernoulli_is_the_cross_entropy_sum():
    """nll_bernoulli equals the summed cross-entropy, and is 4 log 2 for four labels at 0.5."""
    nll_bernoulli = function("nll_bernoulli")
    y = np.array([1.0, 1.0, 0.0, 1.0, 0.0])
    p = np.array([0.8, 0.6, 0.3, 0.9, 0.5])
    expected = -np.sum(y * np.log(p) + (1 - y) * np.log(1 - p))
    assert abs(nll_bernoulli(p, y) - expected) < 1e-12
    assert abs(nll_bernoulli(np.full(4, 0.5), np.array([1.0, 0.0, 1.0, 0.0])) - 4 * np.log(2)) < 1e-12


def test_nll_normal_is_lowest_at_the_mean():
    """For [1, 2, 3, 6] the normal loss at the mean 3 is below the loss at 2 and at 4, and a larger sigma costs n log sigma."""
    nll_normal = function("nll_normal")
    x = np.array([1.0, 2.0, 3.0, 6.0])
    assert nll_normal(x, 3.0, 2.0) < nll_normal(x, 2.0, 2.0) and nll_normal(x, 3.0, 2.0) < nll_normal(x, 4.0, 2.0)
    assert abs(nll_normal(x, 3.0, 1.0) - (0 + 14 / 2)) < 1e-12
