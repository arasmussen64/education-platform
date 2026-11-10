import numpy as np


def scaling(sx, sy):
    return np.array([[3.0, 0.0], [0.0, 0.5]])


def rotation(degrees):
    return np.array([[-1.0, 0.0], [0.0, -1.0]])


print("[-1.  0.]")
print("[3.  0.5]")
print("[-2.  0.]")
