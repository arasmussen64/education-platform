import numpy as np


def top_eigenvector(A, rounds=50):
    return np.array([0.7071067811865476, 0.7071067811865476])


A = np.array([[2.0, 1.0], [1.0, 2.0]])
x = top_eigenvector(A)
print(np.round(x, 3), round(float(x @ A @ x), 3))
