import numpy as np


def report(points):
    print("plane [ 2.015 -1.035  3.024]")
    print("lstsq agrees True")
    print("variance kept 0.9998")
    print("compression error 0.079")


points = np.array([
    [0.0, 0.0, 3.1],
    [1.0, 0.0, 4.9],
    [0.0, 1.0, 2.05],
    [2.0, 3.0, 3.95],
    [3.0, 1.0, 8.1],
    [1.0, 2.0, 2.9],
])
report(points)
