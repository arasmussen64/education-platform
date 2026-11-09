from checks import function, run


def test_program():
    """Prints a 2, b 1, then 0 for a word that was never seen."""
    got = run()
    assert got == "a 2\nb 1\n0\n", f"Your program printed:\n{got}"


def test_count_words():
    """count_words counts a new word from 1 and an empty list gives {}."""
    count_words = function("count_words")
    assert count_words(["x"]) == {"x": 1}, f'count_words(["x"]) returned {count_words(["x"])!r}'
    assert count_words([]) == {}, f"count_words([]) returned {count_words([])!r}"
    assert count_words(["a", "b", "a"]) == {"a": 2, "b": 1}
