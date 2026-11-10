from checks import function, run


def test_the_output():
    """Prints 11, then 12."""
    printed = run()
    assert printed == "11\n12\n", f"Your program printed:\n{printed}"


def test_compose_returns_a_function():
    """compose(f, g) is a function that applies g first, then f, for any f and g."""
    compose = function("compose")
    square_then_negate = compose(lambda x: -x, lambda x: x * x)
    assert callable(square_then_negate)
    assert square_then_negate(3) == -9
    assert compose(str, abs)(-4) == "4"
