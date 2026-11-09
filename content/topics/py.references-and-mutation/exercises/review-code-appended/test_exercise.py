from checks import function

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_appends():
    """appended([1, 2], 3) is [1, 2, 3], and appended([], "a") is ["a"]."""
    appended = function("appended")
    assert appended([1, 2], 3) == [1, 2, 3]
    assert appended([], "a") == ["a"]


def test_new_list():
    """The list given is unchanged, and the result is a different list."""
    appended = function("appended")
    items = [1, 2]
    result = appended(items, 3)
    assert items == [1, 2]
    assert result is not items
