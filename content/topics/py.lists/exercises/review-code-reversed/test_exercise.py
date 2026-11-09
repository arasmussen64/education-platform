from checks import function

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_reverses():
    """reversed_copy([1, 2, 3]) is [3, 2, 1], and reversed_copy([]) is []."""
    reversed_copy = function("reversed_copy")
    assert reversed_copy([1, 2, 3]) == [3, 2, 1]
    assert reversed_copy([]) == []
    assert reversed_copy(["a"]) == ["a"]


def test_original_untouched():
    """The original list is left as it was."""
    reversed_copy = function("reversed_copy")
    original = [1, 2, 3]
    result = reversed_copy(original)
    assert original == [1, 2, 3]
    assert result == [3, 2, 1]
