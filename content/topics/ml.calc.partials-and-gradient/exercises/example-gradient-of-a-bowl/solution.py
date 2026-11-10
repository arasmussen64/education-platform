import numpy as np


def f(p):
    x, y = p
    return x**2 + 3 * y**2


def gradient(p):
    x, y = p
    return np.array([2 * x, 6 * y])


def numeric_gradient(f, p, h=1e-6):
    grad = np.zeros(len(p))
    for i in range(len(p)):
        step = np.zeros(len(p))
        step[i] = h
        grad[i] = (f(p + step) - f(p - step)) / (2 * h)
    return grad


p = np.array([1.0, 1.0])
g = gradient(p)
print(g)
print(np.round(numeric_gradient(f, p), 6))
print(np.allclose(g, numeric_gradient(f, p)))

uphill = g / np.linalg.norm(g)
print(np.round(uphill, 3), round(float(np.linalg.norm(g)), 3))
along = np.array([-6.0, 2.0]) / np.linalg.norm([-6.0, 2.0])
print(round(float(g @ uphill), 3), round(float(g @ along), 3) + 0.0)
print(round(f(p + 0.01 * uphill) - f(p), 4), round(f(p + 0.01 * along) - f(p), 4))
