from solution import rotate


def test_rotates_left():
    """Moves the first item to the end."""
    assert rotate([1, 2, 3]) == [2, 3, 1]


def test_empty_list():
    """Handles an empty list."""
    assert rotate([]) == []
