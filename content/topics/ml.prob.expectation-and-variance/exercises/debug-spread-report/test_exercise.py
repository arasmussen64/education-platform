import numpy as np

from checks import function, run

EXPECTED = 'die 3.5 2.9167 1.708\nprize 2.0 106.0 10.296\n'


def test_the_output():
    """Prints the die's and the prize's mean, variance and standard deviation."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_two_fair_flips():
    """The table of heads in two fair flips has mean 1, variance 0.5 and standard deviation root 0.5."""
    summary = function("summary")
    mean, variance, sd = summary(np.array([0.0, 1.0, 2.0]), np.array([0.25, 0.5, 0.25]))
    assert abs(mean - 1) < 1e-12 and abs(variance - 0.5) < 1e-12 and abs(sd - 0.5**0.5) < 1e-12
