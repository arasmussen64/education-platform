import numpy as np


def standardize(grid):
    return (grid - grid.mean(axis=1, keepdims=True)) / grid.std(axis=1, keepdims=True)


grid = np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]])
print(np.round(standardize(grid), 2))
