def add_bonus(scores, bonus):
    """Return a new list with the bonus added to every score."""
    result = []
    for score in scores:
        result.append(score + bonus)
    return result


def without_lowest(scores):
    """Return a new list without the smallest score."""
    lowest = min(scores)
    result = []
    for score in scores:
        if score != lowest:
            result.append(score)
    return result


def main():
    scores = [70, 55, 90]
    print(f"With bonus: {add_bonus(scores, 5)}")
    print(f"Without lowest: {without_lowest(scores)}")
    print(f"Original: {scores}")


main()
