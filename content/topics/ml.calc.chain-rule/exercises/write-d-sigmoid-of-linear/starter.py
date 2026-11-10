import numpy as np


def slope(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))
