def total(numbers):
    """Return the sum of the numbers."""
    result = 0
    for number in numbers:
        result += number
    return result


def largest(numbers):
    """Return the biggest number."""
    best = 0
    for number in numbers:
        if number > best:
            best = number
    return best


def last_item(items):
    """Return the last item."""
    return items[-1]


def main():
    numbers = [4, 9, 2]
    print(f"Total: {total(numbers)}")
    print(f"Largest: {largest(numbers)}")
    print(f"Last: {last_item(numbers)}")


main()
