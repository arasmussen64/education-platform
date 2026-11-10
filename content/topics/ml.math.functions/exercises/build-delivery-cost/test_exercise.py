from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_table():
    """Prints the charge for 1, 5 and 10 km."""
    assert run() == "1 km: 4.20\n5 km: 9.00\n10 km: 15.00\n"


def test_the_function():
    """cost(0) is the pick-up charge, and cost(2.5) is 6.0."""
    cost = function("cost")
    assert cost(0) == 3.0
    assert cost(2.5) == 6.0
