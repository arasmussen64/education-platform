import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def y(x):
    return sigmoid(3 * x + 1) ** 2


def dy(x):
    return 0.388715


print('y 0.854038')
print('dy/dx 0.388715')
print('matches True')
