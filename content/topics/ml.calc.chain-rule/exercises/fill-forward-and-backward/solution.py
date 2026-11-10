import numpy as np

functions = [lambda x: 3 * x + 1, np.exp, lambda v: 1 / v]
derivatives = [lambda x: 3.0, np.exp, lambda v: -1 / v**2]


def forward(x):
    values = [x]
    for f in functions:
        values.append(f(values[-1]))
    return values


def backward(values):
    grad = 1.0
    for df, v in zip(reversed(derivatives), reversed(values[:-1])):
        grad = grad * df(v)
    return grad


def whole(x):
    return 1 / np.exp(3 * x + 1)


values = forward(0.5)
print(np.round(values, 6))
print(round(float(backward(values)), 6))
print(abs(backward(values) - (whole(0.5 + 1e-6) - whole(0.5 - 1e-6)) / 2e-6) < 1e-6)
