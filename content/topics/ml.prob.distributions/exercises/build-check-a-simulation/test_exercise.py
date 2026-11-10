import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the empirical PMF's start, the gap check and the three fractions."""
    assert run() == 'pmf [0.028 0.121 0.235 0.265]\nlargest gap below 0.003 True\nwithin 1, 2, 3 spreads [0.683 0.954 0.997]\n'


def test_binomial_pmf():
    """Three fair flips give 0.125, 0.375, 0.375, 0.125, and every table sums to 1."""
    binomial_pmf = function("binomial_pmf")
    assert np.allclose([binomial_pmf(k, 3, 0.5) for k in range(4)], [0.125, 0.375, 0.375, 0.125])
    assert abs(sum(binomial_pmf(k, 7, 0.2) for k in range(8)) - 1) < 1e-12


def test_empirical_pmf_and_gap():
    """A hand-made sample gives exact fractions, including an empty slot, and its gap from a formula is what it should be."""
    empirical_pmf = function("empirical_pmf")
    largest_gap = function("largest_gap")
    sample = np.array([0, 1, 1, 2, 2, 2, 2, 0])
    assert np.allclose(empirical_pmf(sample, 3), [0.25, 0.25, 0.5, 0.0])
    # Against n = 3, p = 0.5 the formula is [0.125, 0.375, 0.375, 0.125]; the largest gap is 0.5 - 0.375.
    assert abs(largest_gap(sample, 3, 0.5) - 0.125) < 1e-12


def test_within():
    """Values 0 to 9 around a center of 4.5 with spread 2: 4 of 10 within one spread, 8 within two, all within three."""
    within = function("within")
    assert within(np.arange(10.0), 4.5, 2.0) == [0.4, 0.8, 1.0]
