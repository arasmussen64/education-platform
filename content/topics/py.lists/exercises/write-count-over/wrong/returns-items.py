def count_over(numbers, limit):
    """Return how many numbers are greater than the limit."""
    found = []
    for number in numbers:
        if number > limit:
            found.append(number)
    return found
