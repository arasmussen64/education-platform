import numpy as np


def f(p):
    x, y = p
    return x**2 + 3 * y**2


def numeric_gradient(f, p, h=1e-6):
    grad = np.zeros(len(p))
    for i in range(len(p)):
        grad[i] = (f(p + h) - f(p - h)) / (2 * h)
    return grad


print(np.round(numeric_gradient(f, np.array([1.0, 1.0])), 6))
