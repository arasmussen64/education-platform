def evens(numbers):
    """Return a new list of the even numbers, in order."""
    result = []
    for number in numbers:
        if number % 2 == 1:
            result.append(number)
    return result
