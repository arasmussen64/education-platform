def word_counts(text):
    """Return a dictionary of each word to how many times it appears."""
    counts = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    return counts
