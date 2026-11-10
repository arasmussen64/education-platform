import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def y(x):
    return sigmoid(3 * x + 1) ** 2


def dy(x):
    u = 3 * x + 1
    s = sigmoid(u)
    return 2 * s * (s * (1 - s)) * 3


x = 0.5
print("y", round(float(y(x)), 6))
print("dy/dx", round(float(dy(x)), 6))
numeric = (y(x + 1e-6) - y(x - 1e-6)) / 2e-6
print("matches", abs(dy(x) - numeric) < 1e-6)
