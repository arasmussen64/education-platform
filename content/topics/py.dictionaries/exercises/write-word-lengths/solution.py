def word_lengths(words):
    """Return a dictionary of each word to its length."""
    lengths = {}
    for word in words:
        lengths[word] = len(word)
    return lengths
