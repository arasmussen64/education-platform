def count_words(words):
    """Return a dictionary of each word to how many times it appears."""
    counts = {}
    for word in words:
        counts[word] = counts[word] + 1
    return counts


def main():
    counts = count_words(["a", "b", "a"])
    for word in counts:
        print(word, counts[word])
    print(counts.get("c", 0))


main()
