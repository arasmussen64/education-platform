from checks import function, run


def test_the_output():
    """Prints [1, 3, 6, 10]."""
    printed = run()
    assert printed == "[1, 3, 6, 10]\n", f"Your program printed:\n{printed}"


def test_other_numbers():
    """Works for other numbers, yields one at a time, and yields nothing for an empty list."""
    running_total = function("running_total")
    assert list(running_total([5, -5, 10])) == [5, 0, 10]
    assert list(running_total([])) == []
    first = running_total([2, 3])
    assert next(first) == 2
