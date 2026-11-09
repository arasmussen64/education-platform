from checks import function

# Hidden tests: in a review, the learner sees each docstring and whether it
# passed, but not the failure messages.


def test_middle_column():
    """column([[1, 2, 3], [4, 5, 6]], 1) is [2, 5]."""
    assert function("column")([[1, 2, 3], [4, 5, 6]], 1) == [2, 5]


def test_other_columns():
    """The first and last columns, and an empty grid."""
    column = function("column")
    assert column([[1, 2, 3], [4, 5, 6]], 0) == [1, 4]
    assert column([[1, 2, 3], [4, 5, 6]], 2) == [3, 6]
    assert column([], 0) == []
