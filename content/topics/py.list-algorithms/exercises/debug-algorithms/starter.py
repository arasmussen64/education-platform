def top_three(scores):
    """Return the three highest scores, highest first."""
    ordered = scores.sort(reverse=True)
    return ordered[:2]


def first_position(items, target):
    """Return the position of the first item equal to target, or -1."""
    position = -1
    for i in range(len(items)):
        if items[i] == target:
            position = i
    return position


def main():
    print(top_three([72, 45, 88, 91, 60]))
    print(first_position(["a", "b", "a"], "a"))


main()
