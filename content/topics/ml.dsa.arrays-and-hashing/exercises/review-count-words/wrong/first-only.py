def count_words(text):
    """{word: how many times it appears in the text}."""
    counts = {}
    for word in text.split():
        counts[word] = 1
    return counts


counts = count_words("to be or not to be")
print(counts["to"], counts["be"], counts["or"], len(counts))
