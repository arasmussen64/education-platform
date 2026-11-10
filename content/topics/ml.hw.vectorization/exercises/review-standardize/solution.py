import numpy as np


def standardize(X):
    """Each column minus its mean, divided by its standard deviation, with no Python loop."""
    return (X - X.mean(axis=0)) / X.std(axis=0)


X = np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0], [6.0, 60.0]])
print(np.round(standardize(X), 3))
print(np.allclose(standardize(X).mean(axis=0), 0), np.allclose(standardize(X).std(axis=0), 1))
