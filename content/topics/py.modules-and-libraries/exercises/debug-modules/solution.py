import math
import random
import statistics


def pick(items):
    """Return one of the items, chosen at random."""
    return random.choice(items)


def root(n):
    """Return the square root of n."""
    return math.sqrt(n)


def main():
    print(f"Mean: {statistics.mean([2, 4, 6])}")
    print(f"Root: {root(25)}")
    print(f"Pick ok: {pick(['a', 'b']) in ['a', 'b']}")


if __name__ == "__main__":
    main()
