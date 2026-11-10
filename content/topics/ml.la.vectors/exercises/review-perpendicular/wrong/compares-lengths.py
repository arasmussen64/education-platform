import numpy as np


def is_perpendicular(u, w):
    return bool(np.linalg.norm(u) == np.linalg.norm(w))


print(is_perpendicular(np.array([1.0, 2.0]), np.array([2.0, -1.0])))
print(is_perpendicular(np.array([1.0, 1.0]), np.array([1.0, 2.0])))
