def with_bonus(scores, bonus):
    """Return a new list with the bonus added to every score."""
    result = []
    for score in scores:
        result.append(score + bonus)
