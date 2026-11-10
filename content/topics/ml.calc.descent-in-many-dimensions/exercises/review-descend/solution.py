import numpy as np


def grad(p):
    return 2 * p


def descend(grad, p, rate, steps):
    for step in range(steps):
        p = p - rate * grad(p)
    return p


print(descend(grad, np.array([4.0, 2.0]), 0.25, 3))
