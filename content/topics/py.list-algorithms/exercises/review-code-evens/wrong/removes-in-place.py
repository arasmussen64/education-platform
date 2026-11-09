def evens(numbers):
    """Return a new list of the even numbers, in order."""
    for number in numbers:
        if number % 2 == 1:
            numbers.remove(number)
    return numbers
