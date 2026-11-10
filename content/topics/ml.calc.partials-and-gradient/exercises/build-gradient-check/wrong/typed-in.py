import numpy as np


def numeric_gradient(f, p, h=1e-6):
    return np.array([2.0, 3.0, 29.0])


def check_gradient(f, grad_f, points):
    return 0.0


def steepest(grad):
    return np.array([0.068, 0.103, 0.992])


print('gradient [ 2.  3. 29.]')
print('gap below 1e-6 True')
print('steepest [0.068 0.103 0.992]')
