import numpy as np


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def mse(pred, target):
    return float(np.mean((pred - target) ** 2))


def d_mse(pred, target):
    return 2 * (pred - target) / len(target)


def cross_entropy(p, y, eps=1e-12):
    p = np.clip(p, eps, 1 - eps)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def d_cross_entropy_dz(z, y):
    return sigmoid(z) - y


pred = np.array([2.5, 0.0, 2.1, 7.8])
target = np.array([3.0, -0.5, 2.0, 8.0])
print("mse", round(mse(pred, target), 4))
print("d_mse", np.round(d_mse(pred, target), 3))
p = np.array([0.9, 0.6, 0.3, 0.05])
y = np.array([1.0, 1.0, 0.0, 1.0])
print("cross-entropy", round(cross_entropy(p, y), 3))
z = np.array([2.0, 0.0, -1.0])
y = np.array([1.0, 0.0, 1.0])
print("d/dz", np.round(d_cross_entropy_dz(z, y), 3))
