import numpy as np


def scaling(sx, sy):
    return np.array([[sx, 0.0], [0.0, sy]])


def rotation(degrees):
    t = np.radians(degrees)
    return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])


def compose(*matrices):
    result = np.eye(len(matrices[0]))
    for M in matrices:
        result = result @ M
    return result


def undo(M):
    if abs(np.linalg.det(M)) < 1e-12:
        return None
    return np.linalg.inv(M)


print(np.round(compose(rotation(90), scaling(2, 3)) @ np.array([1.0, 0.0]), 6))
print(np.round(compose(scaling(2, 3), rotation(90)) @ np.array([1.0, 0.0]), 6))
print(undo(np.array([[1.0, 2.0], [2.0, 4.0]])))
