import numpy as np


def derivative(f, x, h=1e-6):
    return (f(x + h) - f(x)) / h


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


checks = [
    ("x**2", lambda x: x**2, lambda x: 2 * x),
    ("exp", np.exp, np.exp),
    ("log", np.log, lambda x: 1 / x),
    ("sigmoid", sigmoid, lambda x: sigmoid(x) * (1 - sigmoid(x))),
]
for name, f, rule in checks:
    gap = max(abs(derivative(f, x) - rule(x)) for x in [0.5, 1.0, 2.0])
    print(name, gap < 1e-6)
