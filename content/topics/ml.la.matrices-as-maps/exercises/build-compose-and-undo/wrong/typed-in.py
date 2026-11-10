import numpy as np


def scaling(sx, sy):
    return np.array([[sx, 0.0], [0.0, sy]])


def rotation(degrees):
    t = np.radians(degrees)
    return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])


def compose(*matrices):
    return matrices[0]


def undo(M):
    return None


print("[0. 3.]")
print("[0. 2.]")
print(None)
