def with_bonus(scores, bonus):
    """Return a new list with the bonus added to every score."""
    for i in range(len(scores)):
        scores[i] = scores[i] + bonus
    return scores
