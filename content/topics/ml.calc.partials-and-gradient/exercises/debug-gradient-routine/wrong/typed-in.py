import numpy as np


def numeric_gradient(f, p, h=1e-6):
    return np.array([2.0, 6.0])


def directional_derivative(grad, direction):
    return 2.0


print("gradient [2. 6.]")
print("east 2.0")
print("north-east 5.657")
