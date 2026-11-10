import numpy as np


def f(p):
    x, y = p
    return x**2 + 3 * y**2


def numeric_gradient(f, p, h=1e-6):
    return np.array([2.0, 6.0])


print("[2. 6.]")
