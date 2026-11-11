from checks import function, run


def test_the_two_errors():
    """Prints 57.0, then 0.0."""
    printed = run()
    assert printed == "57.0\n0.0\n", f"Your program printed:\n{printed}"


def test_error_is_a_mean():
    """error(1, 0, ...) on the same points is 18.0: the misses are 2, 3, 4, 5, 6; their squares add up to 90, and 90 / 5 = 18.0."""
    error = function("error")
    assert error(1, 0, [1, 2, 3, 4, 5], [3, 5, 7, 9, 11]) == 18.0
