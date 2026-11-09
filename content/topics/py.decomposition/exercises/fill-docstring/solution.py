def words_in(text):
    """Return how many words the text has, counting single spaces between them."""
    count = 1
    for ch in text:
        if ch == " ":
            count += 1
    return count


def describe(text):
    """Return a sentence saying how many words the text has."""
    return f"'{text}' has {words_in(text)} words"


def main():
    print(describe("the quick brown fox"))


main()
