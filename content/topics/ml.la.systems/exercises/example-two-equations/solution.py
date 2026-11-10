import numpy as np

# 2x + y = 5
# x - y = 1
A = np.array([[2.0, 1.0], [1.0, -1.0]])
b = np.array([5.0, 1.0])
x = np.linalg.solve(A, b)
print(x)
print(A @ x)
print(np.allclose(A @ x, b))

rows = np.array([[2.0, 1.0, 5.0], [1.0, -1.0, 1.0]])
rows[1] = rows[1] - 0.5 * rows[0]
print(rows)
y = rows[1, 2] / rows[1, 1]
x1 = (rows[0, 2] - rows[0, 1] * y) / rows[0, 0]
print(x1, y)

print(np.linalg.matrix_rank(A))
print(np.linalg.matrix_rank(np.array([[1.0, 2.0], [2.0, 4.0]])))
