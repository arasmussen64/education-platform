from checks import function, run


def test_the_fit():
    """Prints slope 2.0, then intercept 1.0."""
    printed = run()
    assert printed == "slope 2.0\nintercept 1.0\n", f"Your program printed:\n{printed}"


def test_fit_other_points():
    """fit finds the line through (1, 1), (2, 4), (3, 7), (4, 10), (5, 13): slope 3, intercept -2."""
    fit = function("fit")
    assert [round(v, 2) for v in fit([1, 2, 3, 4, 5], [1, 4, 7, 10, 13], 0.05, 2000)] == [3.0, -2.0]
