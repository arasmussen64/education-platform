def doubled(numbers):
    """Return a new list with every number doubled."""
    for i in range(len(numbers)):
        numbers[i] = numbers[i] * 2
    return numbers
