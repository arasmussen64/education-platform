import numpy as np


def chain_derivative(x):
    return np.exp(3 * x)


print(round(float(chain_derivative(0.5)), 6))
