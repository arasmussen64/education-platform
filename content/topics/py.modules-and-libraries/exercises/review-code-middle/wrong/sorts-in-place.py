def middle(numbers):
    """Return the median of a non-empty list of numbers."""
    numbers.sort()
    return numbers[len(numbers) // 2]
