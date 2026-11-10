import numpy as np


def report(grid):
    daily = grid.mean(axis=1)
    print("daily averages:", daily)
    print("above average:")
    print(grid - daily)
    best = grid.sum(axis=1).argmax() + 1
    print("best day:", best)


report(np.array([[15, 25, 55], [25, 35, 45]]))
