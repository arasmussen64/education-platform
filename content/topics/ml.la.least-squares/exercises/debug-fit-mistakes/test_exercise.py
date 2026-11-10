import numpy as np

from checks import function, run

EXPECTED = "slope 1.95\nintercept 1.15\n"


def test_the_output():
    """Prints the slope, then the intercept."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_other_data():
    """Other points give slope 0.25 and intercept about 1.167, in that order."""
    fit_line = function("fit_line")
    slope, intercept = fit_line(np.array([0.0, 2.0, 4.0]), np.array([1.0, 2.0, 2.0]))
    assert np.allclose([slope, intercept], [0.25, 7 / 6])
