import numpy as np


def project(v, onto):
    return (v @ onto) / (v @ v) * v


def rejection(v, onto):
    return v - project(v, onto)


v = np.array([3.0, 4.0])
print(project(v, np.array([1.0, 0.0])))
print(rejection(v, np.array([1.0, 0.0])))
print(project(v, np.array([1.0, 1.0])))
print(rejection(v, np.array([1.0, 1.0])))
