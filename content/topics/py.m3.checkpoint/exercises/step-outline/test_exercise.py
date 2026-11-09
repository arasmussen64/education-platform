from checks import run


def test_four_words():
    """Typing the quick brown fox prints the statistics and four bars."""
    printed = run("the quick brown fox\n")
    assert printed == (
        "Words: 4\nLetters: 16\nLongest word: quick\n###\n#####\n#####\n###\n"
    ), f"Your program printed:\n{printed}"


def test_other_texts():
    """we go far has far as its longest word; hello is one word with one bar."""
    for typed, expected in [
        ("we go far\n", "Words: 3\nLetters: 7\nLongest word: far\n##\n##\n###\n"),
        ("hello\n", "Words: 1\nLetters: 5\nLongest word: hello\n#####\n"),
    ]:
        printed = run(typed)
        assert printed == expected, (
            f"Typing {typed.strip()!r} should print:\n{expected}Your program printed:\n{printed}"
        )
