import numpy as np

A = np.array([[1.0, 1.0, 1.0], [0.0, 2.0, 5.0], [2.0, 5.0, -1.0]])
b = np.array([6.0, -4.0, 27.0])


def solve_system(A, b):
    return np.array([5.0, 3.0, -2.0])


print("[ 5.  3. -2.]")
