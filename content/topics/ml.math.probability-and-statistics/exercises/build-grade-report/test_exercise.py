from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_report():
    """Prints the mean, median and spread of the six scores."""
    assert run() == "Mean: 80.0\nMedian: 77.0\nSpread: 9.2\n"


def test_mean_and_median():
    """mean and median work for other lists, odd counts and unsorted ones included."""
    mean = function("mean")
    median = function("median")
    assert mean([10, 20, 30]) == 20.0
    assert median([9, 1, 5]) == 5
    assert median([1, 2, 3, 100]) == 2.5


def test_spread():
    """spread divides by the number of values, and is 0 when they're all the same."""
    spread = function("spread")
    assert round(spread([10, 20, 30]), 2) == 8.16
    assert spread([4, 4, 4]) == 0
