import numpy as np


def numeric_derivative(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def d_sigmoid(x):
    s = sigmoid(x)
    return s * (1 - s)


def relu(x):
    return np.maximum(x, 0.0)


def d_relu(x):
    return np.where(x > 0, 1.0, 0.0)


def max_error(f, df, xs):
    return sum(abs(df(x) - numeric_derivative(f, x)) for x in xs) / len(xs)


xs = np.array([-2.0, -0.5, 0.5, 2.0])
print("power", max_error(lambda x: x**3, lambda x: 3 * x**2, xs) < 1e-6)
print("exp", max_error(np.exp, np.exp, xs) < 1e-6)
print("sigmoid", max_error(sigmoid, d_sigmoid, xs) < 1e-6)
print("relu", max_error(relu, d_relu, xs) < 1e-6)
