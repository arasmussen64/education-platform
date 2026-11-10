import numpy as np

xs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
ys = np.array([3.0, 5.0, 7.0, 9.0, 11.0])
A = np.column_stack([xs, np.ones(5)])
print(A)
coef = np.linalg.solve(A.T @ A, A.T @ ys)
print(coef)
print(np.linalg.lstsq(A, ys)[0])
print(A @ coef)

ys2 = np.array([3.2, 4.8, 7.1, 9.1, 10.8])
coef2 = np.linalg.solve(A.T @ A, A.T @ ys2)
print(np.round(coef2, 3))
r = ys2 - A @ coef2
print(round(float(r @ xs), 6) + 0.0, round(float(r.sum()), 6) + 0.0)
