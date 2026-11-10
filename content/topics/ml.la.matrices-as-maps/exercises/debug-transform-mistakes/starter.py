import numpy as np


def rotation(degrees):
    t = np.radians(degrees)
    return np.array([[np.cos(t), np.sin(t)], [-np.sin(t), np.cos(t)]])


def corners_after(M, corners):
    for corner in corners:
        # Rounded, and + 0.0 turns a -0. into a plain 0.
        print(np.round(M * corner, 6) + 0.0)


corners = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
corners_after(rotation(90), corners)
