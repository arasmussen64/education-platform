import numpy as np

points = np.array([
    [0.0, 0.0, 3.1],
    [1.0, 0.0, 4.9],
    [0.0, 1.0, 2.05],
    [2.0, 3.0, 3.95],
    [3.0, 1.0, 8.1],
    [1.0, 2.0, 2.9],
])
A = np.column_stack([points[:, 0], points[:, 1], np.ones(6)])
z = points[:, 2]


def loss(w):
    return np.mean((A @ w - z) ** 2)


def gradient(w):
    return 2 / len(z) * (A.T @ (A @ w - z))


w = np.zeros(3)
for step in range(2000):
    w = w - 0.1 * gradient(w)
print("plane", np.round(w, 3))
print("loss", round(float(loss(w)), 4))
