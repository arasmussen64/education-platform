from checks import function, run


def test_the_output():
    """Prints the three counts and the doubling ratio."""
    printed = run()
    assert printed == '45 4950 499500\n4\n', f"Your program printed:\n{printed}"


def test_small_cases():
    """One item makes no comparisons, two make one, five make ten."""
    count_steps = function("count_steps")
    assert (count_steps(1), count_steps(2), count_steps(5)) == (0, 1, 10)
