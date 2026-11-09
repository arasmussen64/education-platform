from checks import function


def test_lengths():
    """word_lengths(["hi", "hello"]) returns {"hi": 2, "hello": 5}."""
    word_lengths = function("word_lengths")
    got = word_lengths(["hi", "hello"])
    assert got == {"hi": 2, "hello": 5}, f"word_lengths returned {got!r}"


def test_empty_and_lookup():
    """An empty list gives {}, and the result can be looked up by word."""
    word_lengths = function("word_lengths")
    assert word_lengths([]) == {}, f"word_lengths([]) returned {word_lengths([])!r}"
    got = word_lengths(["python"])
    assert got["python"] == 6, f"word_lengths(['python']) returned {got!r}"
