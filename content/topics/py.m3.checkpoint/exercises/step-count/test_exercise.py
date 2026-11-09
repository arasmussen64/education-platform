from checks import run


def test_four_words():
    """Typing the quick brown fox prints Words: 4 and Letters: 16."""
    printed = run("the quick brown fox\n")
    assert printed == "Words: 4\nLetters: 16\n", f"Your program printed:\n{printed}"


def test_one_word():
    """Typing hello prints Words: 1 and Letters: 5: the last word counts."""
    printed = run("hello\n")
    assert printed == "Words: 1\nLetters: 5\n", f"Your program printed:\n{printed}"
