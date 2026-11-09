from checks import function, printed

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_inside_and_outside():
    """in_range(5, 1, 10) is True and in_range(0, 1, 10) is False."""
    in_range = function("in_range")
    assert in_range(5, 1, 10) is True
    assert in_range(0, 1, 10) is False
    assert in_range(11, 1, 10) is False


def test_ends_count():
    """Both ends count: in_range(1, 1, 10) and in_range(10, 1, 10) are True."""
    in_range = function("in_range")
    assert in_range(1, 1, 10) is True
    assert in_range(10, 1, 10) is True


def test_returns_quietly():
    """in_range prints nothing."""
    assert printed(function("in_range"), 5, 1, 10) == ""
