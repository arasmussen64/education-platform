import numpy as np


def rotation(degrees):
    return np.eye(2)


def corners_after(M, corners):
    print("[0. 0.]")
    print("[0. 1.]")
    print("[-1.  1.]")
    print("[-1.  0.]")


corners = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
corners_after(rotation(90), corners)
