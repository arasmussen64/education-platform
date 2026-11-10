import numpy as np


def f(p):
    x, y = p
    return x**2 + 3 * y**2


def numeric_gradient(f, p, h=1e-6):
    grad = np.zeros(len(p))
    for i in range(len(p)):
        step = np.zeros(len(p))
        step[i] = h
        grad[i] = (f(p + step) - f(p - step)) / (2 * h)
    return grad


def directional_derivative(grad, direction):
    return grad @ direction / np.linalg.norm(direction)


p = np.array([1.0, 1.0])
g = numeric_gradient(f, p)
print("gradient", np.round(g, 6))
print("east", round(float(directional_derivative(g, np.array([2.0, 0.0]))), 3))
print("north-east", round(float(directional_derivative(g, np.array([3.0, 3.0]))), 3))
