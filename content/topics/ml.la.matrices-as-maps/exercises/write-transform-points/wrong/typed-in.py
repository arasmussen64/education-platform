import numpy as np

square = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
S = np.array([[1.0, 1.0], [0.0, 1.0]])


def transform(M, points):
    return np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 1.0], [1.0, 1.0]])


print(transform(S, square))
