import numpy as np


def least_squares(A, b):
    coef = np.linalg.solve(A, b)
    residual = b - A @ coef
    return coef, float(np.linalg.norm(residual))


def r_squared(A, b):
    coef, _ = least_squares(A, b)
    residual = b - A @ coef
    return float(1 - (residual @ residual) / ((b - b.mean()) @ (b - b.mean())))


xs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
ys = np.array([3.2, 4.8, 7.1, 9.1, 10.8])
A = np.column_stack([xs, np.ones(5)])
coef, length = least_squares(A, ys)
print(np.round(coef, 3), round(length, 3), round(r_squared(A, ys), 3))
