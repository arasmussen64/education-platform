def top_three(scores):
    """Return the three highest scores, highest first."""
    ordered = sorted(scores, reverse=True)
    return ordered[:3]


def first_position(items, target):
    """Return the position of the first item equal to target, or -1."""
    for i in range(len(items)):
        if items[i] == target:
            return i
    return -1


def main():
    print(top_three([72, 45, 88, 91, 60]))
    print(first_position(["a", "b", "a"], "a"))


main()
