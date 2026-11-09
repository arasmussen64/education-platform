def total(numbers):
    """Return the sum of the numbers, 0 for an empty list."""
    result = 0
    for number in numbers:
        result += number
    return result


def largest(numbers):
    """Return the biggest number in a list with at least one item."""
    best = numbers[0]
    for number in numbers:
        if number > best:
            best = number
    return best


def last_item(items):
    """Return the last item of a list with at least one item."""
    return items[-1]


def main():
    numbers = [4, 9, 2]
    print(f"Total: {total(numbers)}")
    print(f"Largest: {largest(numbers)}")
    print(f"Last: {last_item(numbers)}")


main()
