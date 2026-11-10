import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def d_sigmoid(x):
    s = sigmoid(x)
    return s * (1 - s)


print(np.round(d_sigmoid(np.array([-4.0, 0.0, 4.0])), 4))
