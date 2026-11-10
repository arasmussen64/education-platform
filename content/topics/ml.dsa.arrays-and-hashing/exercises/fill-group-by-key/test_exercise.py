from checks import function, run


def test_the_output():
    """Prints the three cities with their counts and totals."""
    printed = run()
    assert printed == 'Oslo 2 38\nLima 2 53\nPune 1 19\n', f"Your program printed:\n{printed}"


def test_every_record_is_kept():
    """Grouping 6 records by a field with 2 values keeps all 6, 3 in each group, in order."""
    group_by = function("group_by")
    records = [{"k": i % 2, "n": i} for i in range(6)]
    groups = group_by(records, "k")
    assert sorted(groups) == [0, 1]
    assert [r["n"] for r in groups[0]] == [0, 2, 4] and [r["n"] for r in groups[1]] == [1, 3, 5]
