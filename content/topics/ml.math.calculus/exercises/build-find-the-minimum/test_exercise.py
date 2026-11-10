from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints Lowest at x = 2.0, loss = 1.0."""
    assert run() == "Lowest at x = 2.0, loss = 1.0\n"


def test_the_slope():
    """slope_at(3) is about 2, and slope_at(2) is about 0."""
    slope_at = function("slope_at")
    assert round(slope_at(3), 3) == 2.0
    assert round(slope_at(2), 3) == 0.0


def test_minimize_from_elsewhere():
    """minimize(-4, 0.2, 40) also ends near 2."""
    minimize = function("minimize")
    assert round(minimize(-4, 0.2, 40), 3) == 2.0
