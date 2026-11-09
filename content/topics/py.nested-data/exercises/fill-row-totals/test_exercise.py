from checks import function


def test_two_rows():
    """row_totals([[1, 2], [3, 4]]) returns [3, 7]."""
    row_totals = function("row_totals")
    got = row_totals([[1, 2], [3, 4]])
    assert got == [3, 7], f"row_totals returned {got!r}"


def test_other_grids():
    """An empty grid gives [], and rows can have different lengths."""
    row_totals = function("row_totals")
    assert row_totals([]) == [], f"row_totals([]) returned {row_totals([])!r}"
    got = row_totals([[5], [1, 1, 1]])
    assert got == [5, 3], f"row_totals([[5], [1, 1, 1]]) returned {got!r}"
