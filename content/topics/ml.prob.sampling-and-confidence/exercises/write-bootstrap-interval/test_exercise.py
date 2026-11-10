import numpy as np

from checks import function, run


def test_the_output():
    """Prints the median and the mean, each with a bootstrap interval."""
    printed = run()
    assert printed == '6.21 (4.21, 10.52)\n10.06 (7.12, 13.34)\n', f"Your program printed:\n{printed}"


def test_properties():
    """The interval brackets the statistic, has positive width, and a constant sample gives a zero-width interval at the constant."""
    bootstrap_interval = function("bootstrap_interval")
    rng = np.random.default_rng(0)
    sample = rng.normal(50, 5, size=30)
    low, high = bootstrap_interval(rng, sample, np.mean)
    assert low < sample.mean() < high and high - low > 1
    assert bootstrap_interval(rng, np.full(10, 7.0), np.median) == (7.0, 7.0)
