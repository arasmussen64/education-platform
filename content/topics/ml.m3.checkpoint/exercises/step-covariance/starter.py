import numpy as np

points = np.array([
    [0.0, 0.0, 3.1],
    [1.0, 0.0, 4.9],
    [0.0, 1.0, 2.05],
    [2.0, 3.0, 3.95],
    [3.0, 1.0, 8.1],
    [1.0, 2.0, 2.9],
])


def covariance(points):
    centered = points - points.mean(axis=...)
    return centered.T @ centered / (len(points) - ...)


print(np.round(covariance(points), 3))
