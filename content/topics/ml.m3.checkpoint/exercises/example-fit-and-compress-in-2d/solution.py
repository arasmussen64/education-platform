import numpy as np

X = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])

A = np.column_stack([X[:, 0], np.ones(6)])
coef = np.linalg.solve(A.T @ A, A.T @ X[:, 1])
print("line", np.round(coef, 3))
print("line residual", round(float(np.linalg.norm(X[:, 1] - A @ coef)), 3))

mean = X.mean(axis=0)
centered = X - mean
C = centered.T @ centered / (len(X) - 1)
values, vectors = np.linalg.eigh(C)
top = vectors[:, -1] * np.sign(vectors[0, -1])
print("top component", np.round(top, 3), "kept", round(float(values[-1] / values.sum()), 4))
scores = centered @ top
rebuilt = np.outer(scores, top) + mean
print("compression error", round(float(np.linalg.norm(X - rebuilt)), 3))
