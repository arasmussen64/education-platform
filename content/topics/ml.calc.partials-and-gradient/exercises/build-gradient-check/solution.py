import numpy as np


def numeric_gradient(f, p, h=1e-6):
    grad = np.zeros(len(p))
    for i in range(len(p)):
        step = np.zeros(len(p))
        step[i] = h
        grad[i] = (f(p + step) - f(p - step)) / (2 * h)
    return grad


def check_gradient(f, grad_f, points):
    return max(np.abs(grad_f(p) - numeric_gradient(f, p)).max() for p in points)


def steepest(grad):
    return grad / np.linalg.norm(grad)


def f(p):
    x, y, z = p
    return x**2 + y * z + z**3


def grad_f(p):
    x, y, z = p
    return np.array([2 * x, z, y + 3 * z**2])


points = [np.array([1.0, 2.0, 3.0]), np.array([0.0, -1.0, 2.0])]
print("gradient", grad_f(points[0]))
print("gap below 1e-6", check_gradient(f, grad_f, points) < 1e-6)
print("steepest", np.round(steepest(grad_f(points[0])), 3))
