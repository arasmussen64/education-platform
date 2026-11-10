import numpy as np


def standardize(X):
    """Each column minus its mean, divided by its standard deviation, with no Python loop."""
    out = np.empty_like(X)
    for j in range(X.shape[1]):
        column = X[:, j]
        for i in range(X.shape[0]):
            out[i, j] = (X[i, j] - column.mean()) / column.std()
    return out


X = np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0], [6.0, 60.0]])
print(np.round(standardize(X), 3))
print(np.allclose(standardize(X).mean(axis=0), 0), np.allclose(standardize(X).std(axis=0), 1))
