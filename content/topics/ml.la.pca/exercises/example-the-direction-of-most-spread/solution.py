import numpy as np

X = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])
mean = X.mean(axis=0)
centered = X - mean
print(mean)
C = centered.T @ centered / (len(X) - 1)
print(np.round(C, 3))
print(np.allclose(C, np.cov(X, rowvar=False)))
values, vectors = np.linalg.eigh(C)
print(np.round(values, 3))
top = vectors[:, -1]
top = top * np.sign(top[0])
print(np.round(top, 3))
scores = centered @ top
print(np.round(scores, 3))
print(np.round(values[-1] / values.sum(), 3))
back = np.outer(scores, top) + mean
print(np.round(back, 2))
