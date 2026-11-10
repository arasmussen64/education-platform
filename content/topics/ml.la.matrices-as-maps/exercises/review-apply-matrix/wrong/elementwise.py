import numpy as np

M = np.array([[0.0, 1.0], [1.0, 0.0]])


def apply(M, v):
    return (M * v).sum(axis=0)


print(apply(M, np.array([3.0, 4.0])))
