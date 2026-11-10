import numpy as np

from checks import function, run


def test_the_output():
    """Prints eight draws and a mean of 0.3."""
    assert run() == '[1 1 0 1 0 0 1 1] 0.3\n'


def test_edges_and_values():
    """p = 0 gives all zeros, p = 1 all ones, and the draws are only 0s and 1s."""
    bernoulli = function("bernoulli")
    rng = np.random.default_rng(9)
    assert bernoulli(rng, 0.0, 50).sum() == 0
    assert bernoulli(rng, 1.0, 50).sum() == 50
    draws = bernoulli(rng, 0.5, 1000)
    assert set(np.unique(draws).tolist()) <= {0, 1}
