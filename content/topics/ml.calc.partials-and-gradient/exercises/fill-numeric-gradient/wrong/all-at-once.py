import numpy as np


def numeric_gradient(f, p, h=1e-6):
    grad = np.zeros(len(p))
    for i in range(len(p)):
        grad[i] = (f(p + h) - f(p - h)) / (2 * h)
    return grad


print(np.round(numeric_gradient(lambda p: p[0] ** 2 + 3 * p[1] ** 2, np.array([1.0, 1.0])), 6))
print(np.round(numeric_gradient(lambda p: p[0] * p[1], np.array([2.0, 3.0])), 6))
print(np.round(numeric_gradient(lambda p: p[0] * p[1] ** 2 + p[2], np.array([1.0, 2.0, 5.0])), 6))
