import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints [2. 0. 1.]."""
    assert run() == "[2. 0. 1.]\n"


def test_other_points():
    """The parabola through (-1, 4), (0, 1), (2, 1) is y = x² - 2x + 1, and it passes through all three."""
    parabola_through = function("parabola_through")
    a, b, c = parabola_through([(-1, 4), (0, 1), (2, 1)])
    assert np.allclose([a, b, c], [1.0, -2.0, 1.0])
    for x, y in [(-1, 4), (0, 1), (2, 1)]:
        assert abs(a * x * x + b * x + c - y) < 1e-9


def test_two_points_share_an_x():
    """Points with a repeated x give None, not an error."""
    parabola_through = function("parabola_through")
    assert parabola_through([(1, 2), (1, 5), (3, 0)]) is None
