def count_words(text):
    count = 1
    for ch in text:
        if ch == " ":
            count += 1
    return count


def longest_word(text):
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
    return f"{count_words(text)} words, longest: {longest_word(text)}"


def main():
    print(summary("the quick brown fox"))
    print(summary("hello"))


main()
