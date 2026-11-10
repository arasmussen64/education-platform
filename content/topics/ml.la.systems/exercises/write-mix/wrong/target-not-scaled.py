import numpy as np


def mix(total, target, low, high):
    A = np.array([[1.0, 1.0], [low, high]])
    b = np.array([total, target])
    return np.linalg.solve(A, b)


print(mix(30, 0.2, 0.1, 0.4))
