def word_counts(text):
    """Return a dictionary of each word to how many times it appears."""
    counts = {}
    for word in text.split():
        counts[word] = 1
    return counts
