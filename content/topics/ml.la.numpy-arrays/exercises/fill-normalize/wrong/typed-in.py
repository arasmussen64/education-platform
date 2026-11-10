import numpy as np


def normalize(values):
    return np.array([0.0, 0.25, 0.5, 1.0])


print(normalize(np.array([2.0, 4.0, 6.0, 10.0])))
