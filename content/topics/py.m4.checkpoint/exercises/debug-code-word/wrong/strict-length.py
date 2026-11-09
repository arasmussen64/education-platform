def has_min_length(word):
    """Return True when the word has at least 5 characters."""
    return len(word) > 5


def has_vowel(word):
    """Return True when the word has at least one vowel: a, e, i, o or u."""
    for ch in word:
        if ch == "a" or ch == "e" or ch == "i" or ch == "o" or ch == "u":
            return True
    return False


def check_word(word):
    """Return OK, or the first problem: too short, then needs a vowel."""
    if not has_min_length(word):
        return "too short"
    if not has_vowel(word):
        return "needs a vowel"
    return "OK"


def test_check_word():
    assert check_word("brave") == "OK"
    assert check_word("cat") == "too short"
    assert check_word("rhythm") == "needs a vowel"
    assert check_word("crypt") == "needs a vowel"
    print("check_word: all checks passed")


def main():
    """Ask for a code word and print the verdict."""
    word = input("Code word? ")
    print(check_word(word))


if __name__ == "__main__":
    test_check_word()
    main()
