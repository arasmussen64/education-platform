import numpy as np

A = np.array([[2.0, 1.0], [1.0, 2.0]])
values, vectors = np.linalg.eigh(A)
print(values)
vectors = vectors * np.sign(vectors[0])
v = vectors[:, 1]
print(np.round(A @ v, 3), np.round(values[1] * v, 3))
print(A @ np.array([1.0, 0.0]))

x = np.array([1.0, 0.0])
for _ in range(5):
    x = A @ x
print(x)
print(np.round(x / np.linalg.norm(x), 3))

R = np.array([[0.0, -1.0], [1.0, 0.0]])
print(np.round(np.sort_complex(np.linalg.eigvals(R)), 6))
