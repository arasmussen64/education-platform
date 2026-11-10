import numpy as np


def slope(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def d_sigmoid(x):
    s = sigmoid(x)
    return s * (1 - s)


print("x**2 at 3:", round(slope(lambda x: x**2, 3.0), 6))
print("sigmoid at 0:", round(float(d_sigmoid(0.0)), 6), round(slope(sigmoid, 0.0), 6))
print("sigmoid at 2:", round(float(d_sigmoid(2.0)), 6), round(slope(sigmoid, 2.0), 6))
