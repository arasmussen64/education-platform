import numpy as np

points = np.array([
    [0.0, 0.0, 3.1],
    [1.0, 0.0, 4.9],
    [0.0, 1.0, 2.05],
    [2.0, 3.0, 3.95],
    [3.0, 1.0, 8.1],
    [1.0, 2.0, 2.9],
])


def design(points):
    return np.column_stack([points[:, 0], points[:, 1], np.ones(len(points))])


A = design(points)
print(A.shape)
print(A[:2])
