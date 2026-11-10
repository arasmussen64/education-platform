import numpy as np


def gaussian_solve(A, b):
    rows = np.hstack([A, b.reshape(-1, 1)]).astype(float)
    n = len(b)
    for col in range(n):
        for r in range(col + 1, n):
            factor = rows[r, col] / rows[col, col]
            rows[r, col:] = rows[r, col:] - factor * rows[col, col:]
    x = np.zeros(n)
    for r in range(n - 1, -1, -1):
        x[r] = (rows[r, n] - rows[r, r + 1 : n] @ x[r + 1 :]) / rows[r, r]
    return x


A = np.array([[2.0, 1.0, -1.0], [-3.0, -1.0, 2.0], [-2.0, 1.0, 2.0]])
b = np.array([8.0, -11.0, -3.0])
print(np.round(gaussian_solve(A, b), 6))
