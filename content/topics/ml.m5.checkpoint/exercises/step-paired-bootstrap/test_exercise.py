import numpy as np

from checks import function, run


def test_the_output():
    """Prints the mean difference, its interval and the comparison with zero."""
    printed = run()
    assert printed == '0.18 0.11 0.255\nTrue\n', f"Your program printed:\n{printed}"


def test_identical_and_better_models():
    """Two identical models differ by exactly zero with a zero-width interval; a model right where the other is wrong gets a positive interval."""
    paired_bootstrap = function("paired_bootstrap")
    correct = np.array([1, 0, 1, 1, 0, 1, 1, 0, 1, 1] * 4)
    assert paired_bootstrap(np.random.default_rng(0), correct, correct) == (0.0, 0.0, 0.0)
    better = np.ones(40, dtype=int)
    mean, low, high = paired_bootstrap(np.random.default_rng(0), better, correct)
    assert abs(mean - 0.3) < 1e-12 and 0 < low <= high
