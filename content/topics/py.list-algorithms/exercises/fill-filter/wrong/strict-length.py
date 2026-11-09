def long_words(words, min_length):
    """Return a new list of the words with at least min_length characters."""
    result = []
    for word in words:
        if len(word) > min_length:
            result.append(word)
    return result
