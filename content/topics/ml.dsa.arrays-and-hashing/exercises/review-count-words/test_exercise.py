from checks import function, run


def test_the_output():
    """Prints 2 2 1 4."""
    assert run() == '2 2 1 4\n'


def test_other_text():
    """An empty text has no words; a repeated word is counted every time."""
    count_words = function("count_words")
    assert count_words("") == {}
    assert count_words("a a a b") == {"a": 3, "b": 1}
