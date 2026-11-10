import numpy as np


def slope(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def d_sigmoid_of_linear(a, b, x):
    s = sigmoid(a * x + b)
    return s * (1 - s)


print(round(float(d_sigmoid_of_linear(2, 1, 2.0)), 6))
print(round(float(d_sigmoid_of_linear(-1, 0, 0.0)), 6))
print(abs(d_sigmoid_of_linear(2, 1, 2.0) - slope(lambda x: sigmoid(2 * x + 1), 2.0)) < 1e-6)
