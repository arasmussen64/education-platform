def count_words(text):
    """Return how many words the text has (words are separated by single spaces)."""
    count = 1
    for ch in text:
        if ch == " ":
            count += 1
    return count


def longest_word(text):
    """Return the longest word in the text, the first one if two tie."""
    word = ""
    longest = ""
    for ch in text:
        if ch == " ":
            if len(word) > len(longest):
                longest = word
            word = ""
        else:
            word = word + ch
    if len(word) > len(longest):
        longest = word
    return longest


def summary(text):
    """Return one line with the word count and the longest word."""
    return f"{count_words(text)} words, longest: {longest_word(text)}"


def main():
    print(summary("the quick brown fox"))
    print(summary("hello"))


main()
