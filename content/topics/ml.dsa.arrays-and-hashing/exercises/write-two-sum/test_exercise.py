from checks import function, run


def test_the_output():
    """Prints the three results."""
    printed = run()
    assert printed == '(9, 11)\nNone\n(8, 8)\n', f"Your program printed:\n{printed}"


def test_more_cases():
    """A number is not paired with itself; the first pair found wins; an empty list gives None."""
    two_sum = function("two_sum")
    assert two_sum([5, 1], 10) is None
    assert two_sum([1, 4, 2, 3, 6], 5) == (1, 4)
    assert two_sum([], 0) is None
