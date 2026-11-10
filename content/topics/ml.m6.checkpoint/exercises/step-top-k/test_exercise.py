from checks import function, run


def test_the_output():
    """Prints the top two and the full order."""
    printed = run()
    assert printed == '[9, 7]\n[9, 7, 7, 3, 3]\n', f"Your program printed:\n{printed}"


def test_ties_keep_the_earlier():
    """Among equal values the earlier record comes first, and k above the length returns everything."""
    top_k = function("top_k")
    records = [{"v": 5, "n": 0}, {"v": 9, "n": 1}, {"v": 5, "n": 2}, {"v": 9, "n": 3}]
    assert [r["n"] for r in top_k(records, "v", 2)] == [1, 3]
    assert [r["n"] for r in top_k(records, "v", 9)] == [1, 3, 0, 2]
