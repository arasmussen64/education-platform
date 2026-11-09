import random


def shuffled(items):
    """Return a new list with the items in random order."""
    result = list(items)
    random.shuffle(result)
    return result
