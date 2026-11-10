import numpy as np

X = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])


def top_share(X):
    centered = X - X.mean(axis=0)
    values = np.linalg.eigvalsh(centered.T @ centered / (len(X) - 1))
    return round(float(values[0] / values.sum()), 3)


print(top_share(X))
