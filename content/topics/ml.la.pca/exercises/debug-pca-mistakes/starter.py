import numpy as np


def report(X):
    C = X.T @ X / (len(X) - 1)
    values, vectors = np.linalg.eigh(C)
    top = vectors[:, 0]
    top = top * np.sign(top[0])
    print("first component explains", round(float(values[-1] / values.sum()), 3))
    print("direction", np.round(top, 3))


X = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])
report(X)
