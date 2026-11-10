import numpy as np


def mse(A, w, z):
    return float(np.mean((A @ w - z) ** 2))


def gradient(A, w, z):
    return 2 / len(z) * (A.T @ (A @ w - z))


def fit_by_descent(A, z, rate, steps):
    w = np.zeros(A.shape[1])
    losses = []
    for step in range(steps):
        losses.append(mse(A, w, z))
        w = w + rate * gradient(A, w, z)
    return w, losses


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
w, losses = fit_by_descent(A, z, 0.1, 2000)
print("plane", np.round(w, 3))
print("lstsq agrees", np.allclose(w, np.linalg.lstsq(A, z)[0], atol=1e-4))
print("loss", round(losses[0], 4), round(losses[10], 4), round(losses[-1], 4))
