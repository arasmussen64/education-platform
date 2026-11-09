import random
import statistics


def roll(sides):
    """Return a random whole number from 1 to sides."""
    return random.randint(1, sides)


def main():
    rolls = []
    for _ in range(5):
        rolls.append(roll(6))
    print(len(rolls), "rolls, all between 1 and 6:", min(rolls) >= 1 and max(rolls) <= 6)
    print("Mean of 2, 4, 9:", statistics.mean([2, 4, 9]))
    print("A random pick is one of the options:", random.choice(["a", "b"]) in ["a", "b"])


if __name__ == "__main__":
    main()
