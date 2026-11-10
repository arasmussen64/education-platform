import numpy as np


def center(X):
    """Subtract each column's own mean, so every column sums to 0."""
    return X - X.mean()


def score(X, w):
    """The weighted sum of each row: one score per row, with one weight per column."""
    return (X * w).sum(axis=1)


X = np.arange(18, dtype=np.float64).reshape(6, 3)
w = np.array([0.5, -1.0, 2.0]).reshape(-1, 1)
centered = center(X)
print("column sums after centering:", centered.sum(axis=0))
print("scores:", score(centered, w))
