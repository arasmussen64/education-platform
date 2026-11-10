import numpy as np


def scaling(sx, sy):
    return np.array([[sx, 0.0], [0.0, ...]])


def rotation(degrees):
    t = np.radians(...)
    return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), ...]])


print(np.round(rotation(180) @ np.array([1.0, 0.0]), 6))
print(scaling(3, 0.5) @ np.array([1.0, 1.0]))
print(np.round(rotation(90) @ np.array([0.0, 2.0]), 6))
