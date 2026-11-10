from checks import function, run


def test_slopes_at_zero():
    """Prints -50.0, then -14.0."""
    printed = run()
    assert printed == "-50.0\n-14.0\n", f"Your program printed:\n{printed}"


def test_slopes_at_the_answer():
    """At m = 2, b = 1 the line is right, so both slopes are 0."""
    slopes = function("slopes")
    assert slopes(2, 1, [1, 2, 3, 4, 5], [3, 5, 7, 9, 11]) == [0.0, 0.0]
