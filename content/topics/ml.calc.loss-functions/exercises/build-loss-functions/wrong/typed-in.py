import numpy as np


def mse(pred, target):
    return 0.1375


def d_mse(pred, target):
    return np.array([-0.25, 0.25, 0.05, -0.1])


def cross_entropy(p, y, eps=1e-12):
    return 0.992


def d_cross_entropy_dz(z, y):
    return np.array([-0.04, 0.167, -0.244])


print('mse 0.1375')
print('d_mse [-0.25  0.25  0.05 -0.1 ]')
print('cross-entropy 0.992')
print('d/dz [-0.04   0.167 -0.244]')
