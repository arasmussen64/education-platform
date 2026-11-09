def reversed_copy(items):
    """Return a new list with the items in reverse order."""
    result = []
    for i in range(len(items) - 1, -1, -1):
        result.append(items[i])
    return result
