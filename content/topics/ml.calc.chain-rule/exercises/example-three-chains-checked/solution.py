import numpy as np


def slope(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


x = 2.0
u = 3 * x + 1
print(2 * u * 3, round(slope(lambda x: (3 * x + 1) ** 2, x), 6))

u = 2 * x + 1
s = sigmoid(u)
print(round(float(s * (1 - s) * 2), 6), round(slope(lambda x: sigmoid(2 * x + 1), x), 6))

u = 2 * x
v = np.exp(u)
w = 1 + v
y = np.log(w)
print(round(float(y), 6))
print(2, round(float(v), 6), 1, round(float(1 / w), 6))
print(round(float(2 * v * 1 * (1 / w)), 6), round(slope(lambda x: np.log(1 + np.exp(2 * x)), x), 6))

grad = 1.0
for local in [1 / w, 1, v, 2]:
    grad = grad * local
print(round(float(grad), 6))
