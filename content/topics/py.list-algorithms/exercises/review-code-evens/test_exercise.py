from checks import function

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_keeps_evens():
    """evens([1, 2, 3, 4]) is [2, 4], evens([1, 3]) is [], and evens([]) is []."""
    evens = function("evens")
    assert evens([1, 2, 3, 4]) == [2, 4]
    assert evens([1, 3]) == []
    assert evens([]) == []


def test_original_unchanged():
    """The list passed in is left as it was."""
    evens = function("evens")
    original = [2, 3, 4]
    assert evens(original) == [2, 4]
    assert original == [2, 3, 4]
