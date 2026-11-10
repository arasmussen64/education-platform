import numpy as np

M = np.array([[0.0, 1.0], [1.0, 0.0]])


def apply(M, v):
    return M @ v


print(apply(M, np.array([3.0, 4.0])))
