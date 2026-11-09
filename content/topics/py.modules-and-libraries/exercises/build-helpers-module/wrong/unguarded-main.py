import random
import statistics


def mean_of(numbers):
    """Return the mean."""
    return statistics.mean(numbers)


def spread(numbers):
    """Return the spread."""
    return max(numbers) - min(numbers)


def pick(items):
    """Return a random item."""
    return random.choice(items)


def dice(count, sides):
    """Return count rolls."""
    rolls = []
    for _ in range(count):
        rolls.append(random.randint(1, sides))
    return rolls


def main():
    numbers = [2, 4, 9]
    print(f"Mean: {mean_of(numbers)}")
    print(f"Spread: {spread(numbers)}")


main()
