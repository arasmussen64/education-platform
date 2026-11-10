import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the standard error, the interval, the coverage and the bootstrap interval."""
    assert run() == 'standard error 1.13\ninterval [ 6.17 10.59]\ncoverage 0.934\nmedian 6.09 [4.08 8.12]\n'


def test_standard_error_and_interval():
    """[2, 4, 4, 4, 5, 5, 7, 9] has standard error 0.756; its z = 2 interval is the mean plus or minus 1.512."""
    standard_error = function("standard_error")
    confidence_interval = function("confidence_interval")
    sample = np.array([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    assert abs(standard_error(sample) - 0.756) < 0.001
    low, high = confidence_interval(sample, z=2)
    assert abs(low - (5 - 1.512)) < 0.002 and abs(high - (5 + 1.512)) < 0.002


def test_coverage_of_a_normal_population():
    """For samples of 30 from a normal, the 95 percent interval covers the true mean between 92 and 98 percent of the time."""
    coverage = function("coverage")
    rng = np.random.default_rng(1)
    fraction = coverage(rng, lambda rng, n: rng.normal(5, 2, size=n), 5, 30, 1000)
    assert 0.92 <= fraction <= 0.98


def test_bootstrap():
    """A constant sample gives a zero-width interval; a spread-out one brackets its mean."""
    bootstrap_interval = function("bootstrap_interval")
    rng = np.random.default_rng(2)
    assert bootstrap_interval(rng, np.full(12, 3.0), np.mean) == (3.0, 3.0)
    sample = rng.normal(0, 1, size=40)
    low, high = bootstrap_interval(rng, sample, np.mean)
    assert low < sample.mean() < high
