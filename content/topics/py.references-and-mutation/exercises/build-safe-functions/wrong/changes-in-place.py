def add_bonus(scores, bonus):
    """Return the scores with the bonus added."""
    for i in range(len(scores)):
        scores[i] += bonus
    return scores


def without_lowest(scores):
    """Return the scores without the smallest."""
    scores.remove(min(scores))
    return scores


def main():
    scores = [70, 55, 90]
    print(f"With bonus: {add_bonus(list(scores), 5)}")
    print(f"Without lowest: {without_lowest(list(scores))}")
    print(f"Original: {scores}")


main()
