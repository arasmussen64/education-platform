import numpy as np


def explained(X):
    centered = X - X.mean(axis=0) * 0
    C = centered.T @ centered / (len(X) - 1)
    values = np.linalg.eigvalsh(C)[::-1]
    return np.round(values / values.sum(), 3)


X = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])
print(explained(X))
print(explained(np.array([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0], [4.0, 4.0]])))
