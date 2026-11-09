import random
import statistics


def mean_of(numbers):
    """Return the mean of a non-empty list of numbers."""
    return statistics.mean(numbers)


def spread(numbers):
    """Return the biggest number minus the smallest."""
    return max(numbers) - min(numbers)


def pick(items):
    """Return one of the items, chosen at random."""
    return random.choice(items)


def dice(count, sides):
    """Return count random whole numbers, each from 1 to sides."""
    rolls = []
    for _ in range(count):
        rolls.append(random.randint(1, sides))
    return rolls


def main():
    numbers = [2, 4, 9]
    print(f"Mean: {mean_of(numbers)}")
    print(f"Spread: {spread(numbers)}")


if __name__ == "__main__":
    main()
