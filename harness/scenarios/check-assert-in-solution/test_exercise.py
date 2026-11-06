from solution import average


def test_average():
    """Averages a list of numbers."""
    assert average([2, 4]) == 3


def test_empty():
    """Handles an empty list."""
    average([])
