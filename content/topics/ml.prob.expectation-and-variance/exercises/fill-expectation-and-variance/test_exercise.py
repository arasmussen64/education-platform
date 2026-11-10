import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three tables' moments."""
    printed = run()
    assert printed == '3.5 2.9167\n0.3 0.21\n2.5 3.25\n', f"Your program printed:\n{printed}"


def test_a_certain_value_and_a_binomial():
    """A variable that is always 4 has mean 4 and variance 0; the table of two fair flips has mean 1 and variance 0.5."""
    expectation = function("expectation")
    variance = function("variance")
    assert expectation(np.array([4.0]), np.array([1.0])) == 4 and variance(np.array([4.0]), np.array([1.0])) == 0
    flips = np.array([0.0, 1.0, 2.0])
    probs = np.array([0.25, 0.5, 0.25])
    assert abs(expectation(flips, probs) - 1) < 1e-12 and abs(variance(flips, probs) - 0.5) < 1e-12
