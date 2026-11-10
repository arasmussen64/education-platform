import numpy as np


def mse(pred, target):
    return float(np.mean((pred - target) ** 2))


def cross_entropy(p, y):
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


pred = np.array([2.5, 0.0, 2.1, 7.8])
target = np.array([3.0, -0.5, 2.0, 8.0])
print("mse", round(mse(pred, target), 4))
p = np.array([0.9, 0.6, 0.3, 0.05])
y = np.array([1.0, 1.0, 0.0, 1.0])
print("cross-entropy", round(cross_entropy(p, y), 3))
