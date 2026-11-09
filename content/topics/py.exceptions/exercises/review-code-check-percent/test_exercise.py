from checks import function

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_in_range():
    """check_percent returns 0, 50 and 100 unchanged."""
    check_percent = function("check_percent")
    assert check_percent(0) == 0
    assert check_percent(50) == 50
    assert check_percent(100) == 100


def test_out_of_range():
    """check_percent raises ValueError saying out of range for -1 and 101."""
    check_percent = function("check_percent")
    for bad in (-1, 101):
        raised = False
        try:
            check_percent(bad)
        except ValueError as error:
            raised = str(error) == "out of range"
        assert raised
