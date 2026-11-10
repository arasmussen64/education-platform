import numpy as np

A = np.array([[1.0, 1.0, 1.0], [0.0, 2.0, 5.0], [2.0, 5.0, -1.0]])
b = np.array([6.0, -4.0, 27.0])


def solve_system(A, b):
    return np.round(np.linalg.solve(A, b), 6)


print(solve_system(A, b))
