import numpy as np


def predict(X, w, b):
    """One score per row: the weighted sum of its columns plus a bias."""
    return np.array([sum(x * weight for x, weight in zip(row, w)) + b for row in X])


def standardize(X):
    """Each column minus its mean, over its standard deviation; a column with no spread becomes zeros."""
    spread = X.std(axis=0)
    return (X - X.mean(axis=0)) / np.where(spread == 0, 1.0, spread)


def relu(x):
    """x where positive, 0 elsewhere."""
    return np.maximum(x, 0.0)


def running_max(x):
    """The largest value seen so far at each position: a loop in C, not in Python."""
    return np.maximum.accumulate(x)


def ema(X, alpha):
    """An exponential moving average down the rows: each row needs the one before, so the rows loop and the columns don't."""
    state = np.zeros(X.shape[1])
    out = np.empty_like(X)
    for t in range(len(X)):
        state = alpha * X[t] + (1 - alpha) * state
        out[t] = state
    return out


X = np.arange(12, dtype=np.float64).reshape(4, 3)
w = np.array([1.0, -1.0, 0.5])
print(predict(X, w, 2.0))
print(np.round(standardize(X), 3))
print(relu(np.array([-1.0, 0.0, 2.5])), running_max(np.array([1.0, 3.0, 2.0, 5.0, 4.0])))
print(np.round(ema(X, 0.5), 3))
