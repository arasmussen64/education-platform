def total(numbers):
    """Return the sum of the numbers."""
    return sum(numbers)


def largest(numbers):
    """Return the biggest number."""
    return max(numbers)


def last_item(items):
    """Return the last item."""
    return items[-1]


def main():
    numbers = [4, 9, 2]
    print(f"Total: {total(numbers)}")
    print(f"Largest: {largest(numbers)}")
    print(f"Last: {last_item(numbers)}")


main()
