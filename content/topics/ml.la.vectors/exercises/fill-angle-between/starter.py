import numpy as np


def angle_degrees(u, w):
    cos = (u @ w) / (np.linalg.norm(u) * ...)
    cos = np.clip(cos, -1.0, 1.0)
    return round(float(np.degrees(np.arccos(...))), 2)


print(angle_degrees(np.array([1.0, 0.0]), np.array([1.0, 1.0])))
print(angle_degrees(np.array([1.0, 0.0]), np.array([0.0, 1.0])))
