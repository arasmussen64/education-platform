import numpy as np

points = np.array([
    [0.0, 0.0, 3.1],
    [1.0, 0.0, 4.9],
    [0.0, 1.0, 2.05],
    [2.0, 3.0, 3.95],
    [3.0, 1.0, 8.1],
    [1.0, 2.0, 2.9],
])


def shares(points):
    centered = points - points.mean(axis=0)
    C = centered.T @ centered / (len(points) - 1)
    values = np.linalg.eigvalsh(C)[...]
    return values / ...


print(np.round(shares(points), 3))
