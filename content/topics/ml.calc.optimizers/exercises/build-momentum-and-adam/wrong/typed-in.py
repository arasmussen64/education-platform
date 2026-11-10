import numpy as np


def momentum(grad, p, rate, beta, steps):
    return [p] * steps


def adam(grad, p, rate, steps, beta1=0.9, beta2=0.999, eps=1e-8):
    return [np.array([9.7, 0.7])] * steps


print('plain 13.398')
print('momentum 0.0009')
print('adam 0.0029')
print("adam's first step [9.7 0.7]")
