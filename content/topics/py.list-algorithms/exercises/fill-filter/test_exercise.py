from checks import function


def test_keeps_long_words():
    """long_words(["hi", "there", "you", "hello"], 4) returns ["there", "hello"]."""
    long_words = function("long_words")
    got = long_words(["hi", "there", "you", "hello"], 4)
    assert got == ["there", "hello"], f"long_words returned {got!r}"


def test_edges():
    """An empty list gives an empty list, and a word exactly min_length long is kept."""
    long_words = function("long_words")
    assert long_words([], 3) == [], f"long_words([], 3) returned {long_words([], 3)!r}"
    assert long_words(["abc", "ab"], 3) == ["abc"], (
        f'long_words(["abc", "ab"], 3) returned {long_words(["abc", "ab"], 3)!r}'
    )
