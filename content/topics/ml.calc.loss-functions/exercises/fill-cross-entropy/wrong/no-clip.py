import numpy as np


def cross_entropy(p, y, eps=1e-12):
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


print(round(cross_entropy(np.array([0.9, 0.6, 0.3, 0.05]), np.array([1.0, 1.0, 0.0, 1.0])), 3))
print(round(cross_entropy(np.array([1.0, 0.0]), np.array([1.0, 0.0])), 6))
print(round(cross_entropy(np.array([0.0]), np.array([1.0])), 3))
