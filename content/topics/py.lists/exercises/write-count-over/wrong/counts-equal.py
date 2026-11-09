def count_over(numbers, limit):
    """Return how many numbers are greater than the limit."""
    count = 0
    for number in numbers:
        if number >= limit:
            count += 1
    return count
