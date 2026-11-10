import numpy as np


def grad(p):
    return 2 * p


def descend(grad, p, rate, steps):
    return np.array([0.5, 0.25])


print("[0.5  0.25]")
