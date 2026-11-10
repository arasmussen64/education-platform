import numpy as np


def top_eigenvector(A, rounds=50):
    x = np.ones(len(A))
    for _ in range(rounds):
        x = A @ x
        x = x / np.linalg.norm(x)
    return x


A = np.array([[2.0, 1.0], [1.0, 2.0]])
x = top_eigenvector(A)
print(np.round(x, 3), round(float(x @ A @ x), 3))
