from checks import run


def test_four_words():
    """Typing the quick brown fox prints the statistics and four bars."""
    printed = run("the quick brown fox\n")
    assert printed == (
        "Words: 4\nLetters: 16\nLongest word: quick\n###\n#####\n#####\n###\n"
    ), f"Your program printed:\n{printed}"


def test_one_word():
    """Typing hello prints the statistics and one bar of five, on its own line."""
    printed = run("hello\n")
    assert printed == "Words: 1\nLetters: 5\nLongest word: hello\n#####\n", (
        f"Your program printed:\n{printed}"
    )
