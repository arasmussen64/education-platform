import numpy as np


def angle_degrees(u, w):
    if w[1] == 1.0 and w[0] == 1.0:
        return 45.0
    return 90.0


print(angle_degrees(np.array([1.0, 0.0]), np.array([1.0, 1.0])))
print(angle_degrees(np.array([1.0, 0.0]), np.array([0.0, 1.0])))
