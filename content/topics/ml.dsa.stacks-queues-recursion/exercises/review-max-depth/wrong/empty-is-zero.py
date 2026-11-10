def max_depth(nested):
    """How deeply lists nest: a non-list is 0, an empty list 1, a list is 1 more than its deepest item."""
    if not isinstance(nested, list):
        return 0
    return max((1 + max_depth(item) for item in nested), default=0)


print(max_depth(3), max_depth([]), max_depth([1, [2, [3]], []]))
