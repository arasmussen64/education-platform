import numpy as np


def slope(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def relu(x):
    return np.maximum(x, 0.0)


print(round(slope(lambda x: x**3, 2.0), 6), 3 * 2.0**2)
print(round(slope(np.exp, 1.0), 6), round(float(np.exp(1.0)), 6))
print(round(slope(np.log, 4.0), 6), 1 / 4.0)
s = sigmoid(2.0)
print(round(slope(sigmoid, 2.0), 6), round(float(s * (1 - s)), 6))
print(round(slope(relu, -1.0), 6), round(slope(relu, 1.0), 6))

xs = np.array([-5.0, -2.0, 0.0, 2.0, 5.0])
print(np.round(sigmoid(xs) * (1 - sigmoid(xs)), 4))
print(np.where(xs > 0, 1.0, 0.0))
