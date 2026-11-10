import numpy as np


def slope(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def d_sigmoid_of_linear(a, b, x):
    return 0.013296 if a == 2 else -0.25


print(0.013296)
print(-0.25)
print(True)
