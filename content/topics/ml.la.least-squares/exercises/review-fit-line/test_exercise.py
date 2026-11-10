import numpy as np

from checks import function, run


def test_the_output():
    """Prints [1.95 1.15]."""
    assert run() == "[1.95 1.15]\n"


def test_exact_data():
    """Points on y = 2x + 1 give exactly slope 2, intercept 1."""
    fit_line = function("fit_line")
    assert np.allclose(fit_line(np.array([1.0, 2.0, 3.0]), np.array([3.0, 5.0, 7.0])), [2.0, 1.0])
