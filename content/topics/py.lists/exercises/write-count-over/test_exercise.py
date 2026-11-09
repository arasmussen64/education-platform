from checks import function


def test_some_over():
    """count_over([3, 8, 10, 1], 5) returns 2."""
    count_over = function("count_over")
    assert count_over([3, 8, 10, 1], 5) == 2, (
        f"count_over([3, 8, 10, 1], 5) returned {count_over([3, 8, 10, 1], 5)!r}"
    )


def test_none_over():
    """count_over([], 5) returns 0, and so does count_over([5, 5], 5): equal doesn't count."""
    count_over = function("count_over")
    assert count_over([], 5) == 0, f"count_over([], 5) returned {count_over([], 5)!r}"
    assert count_over([5, 5], 5) == 0, f"count_over([5, 5], 5) returned {count_over([5, 5], 5)!r}"
