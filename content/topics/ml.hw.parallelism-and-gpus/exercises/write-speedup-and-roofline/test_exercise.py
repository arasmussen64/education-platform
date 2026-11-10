from checks import function, run


def test_the_output():
    """Prints the speed-ups and the two roofline times."""
    printed = run()
    assert printed == '4.71 10.0\n214.7\n24.0\n', f"Your program printed:\n{printed}"


def test_limits():
    """Fully parallel work speeds up by the worker count, fully serial work not at all, and the roofline picks the longer time either way round."""
    speedup = function("speedup")
    roofline_seconds = function("roofline_seconds")
    assert abs(speedup(1.0, 16) - 16) < 1e-9 and abs(speedup(0.0, 16) - 1) < 1e-9
    assert abs(roofline_seconds(1e9, 1e6, 1e12, 1e9) - 1e-3) < 1e-12
    assert abs(roofline_seconds(1e6, 1e9, 1e12, 1e9) - 1.0) < 1e-12
