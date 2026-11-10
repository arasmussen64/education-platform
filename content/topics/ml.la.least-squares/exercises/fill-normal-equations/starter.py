import numpy as np


def fit_line(xs, ys):
    A = np.column_stack([xs, np.ones(...)])
    return np.linalg.solve(A.T @ A, A.T @ ...)


print(fit_line(np.array([1.0, 2.0, 3.0, 4.0, 5.0]), np.array([3.0, 5.0, 7.0, 9.0, 11.0])))
print(np.round(fit_line(np.array([1.0, 2.0, 3.0, 4.0, 5.0]), np.array([3.2, 4.8, 7.1, 9.1, 10.8])), 3))
