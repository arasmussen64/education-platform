def passing(scores, cutoff):
    """Return a new list of the scores that are at least the cutoff, in order."""
    result = []
    for score in scores:
        if score >= cutoff:
            result.append(score)
    return result


def position_of(items, target):
    """Return the position of the first item equal to target, or -1."""
    for i in range(len(items)):
        if items[i] == target:
            return i
    return -1


def top_three(scores):
    """Return a new list of the three highest scores, highest first."""
    return sorted(scores, reverse=True)[:3]


def main():
    scores = [72, 45, 88, 91, 60]
    print(f"Passing: {passing(scores, 60)}")
    print(f"Position of 88: {position_of(scores, 88)}")
    print(f"Top three: {top_three(scores)}")


main()
