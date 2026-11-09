from checks import function

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_median():
    """middle([3, 1, 10]) is 3, and middle([1, 2, 3, 40]) is 2.5."""
    middle = function("middle")
    assert middle([3, 1, 10]) == 3
    assert middle([1, 2, 3, 40]) == 2.5


def test_leaves_list_alone():
    """The list given is unchanged."""
    numbers = [3, 1, 10]
    function("middle")(numbers)
    assert numbers == [3, 1, 10]
