import numpy as np


def forward(functions, x):
    values = [x]
    for f in functions:
        values.append(f(values[-1]))
    return values


def backward(derivatives, values):
    grad = 1.0
    for df, v in zip(reversed(derivatives), reversed(values[:-1])):
        grad = grad + df(v)
    return grad


def chain_derivative(functions, derivatives, x):
    return backward(derivatives, forward(functions, x))


def numeric(functions, x, h=1e-6):
    return (forward(functions, x + h)[-1] - forward(functions, x - h)[-1]) / (2 * h)


functions = [lambda x: 2 * x, np.exp, lambda v: 1 + v, np.log]
derivatives = [lambda x: 2.0, np.exp, lambda v: 1.0, lambda w: 1 / w]
d = chain_derivative(functions, derivatives, 2.0)
print(round(float(d), 6), abs(d - numeric(functions, 2.0)) < 1e-6)
