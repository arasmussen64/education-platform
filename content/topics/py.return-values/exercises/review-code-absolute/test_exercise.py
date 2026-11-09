from checks import function, printed

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_negative():
    """absolute(-5) returns 5."""
    assert function("absolute")(-5) == 5


def test_positive_and_zero():
    """absolute(3) returns 3, and absolute(0) returns 0."""
    absolute = function("absolute")
    assert absolute(3) == 3
    assert absolute(0) == 0


def test_returns_quietly():
    """absolute returns its answer and prints nothing."""
    assert printed(function("absolute"), -2) == ""
