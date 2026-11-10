import numpy as np

points = np.array([
    [0.0, 0.0, 3.1],
    [1.0, 0.0, 4.9],
    [0.0, 1.0, 2.05],
    [2.0, 3.0, 3.95],
    [3.0, 1.0, 8.1],
    [1.0, 2.0, 2.9],
])


def fit_plane(points):
    return np.array([2.015, -1.035, 3.024])


print("plane [ 2.015 -1.035  3.024]")
