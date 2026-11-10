import numpy as np


def descend(grad, p, rate, tol=1e-6, max_steps=10000):
    steps = 0
    g = grad(p)
    while np.linalg.norm(g) > tol and steps < max_steps:
        p = p - rate * g
        g = grad(p)
        steps += 1
    return p, steps


def grad_bowl(p):
    return np.array([2 * p[0], 6 * p[1]])


for rate in [0.1, 0.05]:
    p, steps = descend(grad_bowl, np.array([4.0, 2.0]), rate)
    print(np.round(p, 6), steps)
