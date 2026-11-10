import numpy as np

from checks import function, run


def test_the_output():
    """Prints 2.0 and 3.5."""
    assert run() == '2.0\n3.5\n'


def test_other_tables():
    """A Bernoulli(0.25) has expectation 0.25; a certain 7 has expectation 7."""
    expectation = function("expectation")
    assert abs(expectation(np.array([0.0, 1.0]), np.array([0.75, 0.25])) - 0.25) < 1e-12
    assert expectation(np.array([7.0]), np.array([1.0])) == 7
