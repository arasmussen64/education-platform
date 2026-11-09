from checks import function


def test_doubles():
    """doubled([1, 2, 3]) returns [2, 4, 6], and doubled([]) returns []."""
    doubled = function("doubled")
    assert doubled([1, 2, 3]) == [2, 4, 6], f"doubled([1, 2, 3]) returned {doubled([1, 2, 3])!r}"
    assert doubled([]) == [], f"doubled([]) returned {doubled([])!r}"


def test_original_unchanged():
    """The list passed in is left as it was."""
    doubled = function("doubled")
    original = [5, 6]
    result = doubled(original)
    assert original == [5, 6], f"the original list became {original!r}"
    assert result == [10, 12], f"doubled([5, 6]) returned {result!r}"
