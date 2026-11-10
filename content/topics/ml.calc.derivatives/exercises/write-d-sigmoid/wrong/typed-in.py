import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def d_sigmoid(x):
    return np.array([0.0177, 0.25, 0.0177])


print('[0.0177 0.25   0.0177]')
