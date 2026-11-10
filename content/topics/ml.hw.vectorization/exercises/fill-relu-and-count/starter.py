import numpy as np

x = np.array([-2.0, -0.5, 0.0, 1.5, 3.0, -1.0])


def relu(x):
    """x where it is positive and 0 elsewhere, with no Python loop: a mask picks, np.where chooses."""
    return np.where(..., x, 0.0)


def count_positive(x):
    """How many entries are positive: a boolean array summed (True counts as 1)."""
    return int((...).sum())


print(relu(x), count_positive(x))
