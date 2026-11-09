from checks import run


def test_four_words():
    """Typing the quick brown fox prints the three statistics, with quick as the longest word."""
    printed = run("the quick brown fox\n")
    assert printed == "Words: 4\nLetters: 16\nLongest word: quick\n", (
        f"Your program printed:\n{printed}"
    )


def test_last_word_longest():
    """Typing we go far ends with Longest word: far: the last word is compared too."""
    printed = run("we go far\n")
    assert printed == "Words: 3\nLetters: 7\nLongest word: far\n", (
        f"Your program printed:\n{printed}"
    )


def test_middle_word_longest():
    """Typing a journey begins ends with Longest word: journey."""
    printed = run("a journey begins\n")
    assert printed == "Words: 3\nLetters: 14\nLongest word: journey\n", (
        f"Your program printed:\n{printed}"
    )
