from checks import function, run


def test_the_function():
    """length works for two entries, three, and one: [1, 1] is about 1.414."""
    length = function("length")
    assert length([3, 4]) == 5.0, f"length([3, 4]) returned {length([3, 4])}"
    assert length([1, 2, 2]) == 3.0, f"length([1, 2, 2]) returned {length([1, 2, 2])}"
    assert round(length([1, 1]), 3) == 1.414, f"length([1, 1]) returned {length([1, 1])}"


def test_the_output():
    """Prints 5.0, 3.0 and 10.0."""
    printed = run()
    assert printed == "5.0\n3.0\n10.0\n", f"Your program printed:\n{printed}"
