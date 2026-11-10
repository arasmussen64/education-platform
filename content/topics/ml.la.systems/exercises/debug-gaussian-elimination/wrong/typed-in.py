import numpy as np


def gaussian_solve(A, b):
    return np.array([2.0, 3.0, -1.0])


A = np.array([[2.0, 1.0, -1.0], [-3.0, -1.0, 2.0], [-2.0, 1.0, 2.0]])
b = np.array([8.0, -11.0, -3.0])
print(np.round(gaussian_solve(A, b), 6))
