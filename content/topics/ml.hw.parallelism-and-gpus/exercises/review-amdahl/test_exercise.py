from checks import function, run


def test_the_output():
    """Prints the three speed-ups."""
    assert run() == '2.5 4.71 5.0\n'


def test_limits():
    """Fully parallel work speeds up by the worker count; a tenth serial never passes 10."""
    speedup = function("speedup")
    assert abs(speedup(1.0, 7) - 7) < 1e-9 and speedup(0.9, 10**6) < 10 and speedup(0.9, 10**6) > 9.99
