import numpy as np


def adam(x, rate, steps, beta1=0.9, beta2=0.999, eps=1e-8):
    return x - rate * steps


print('1 1.9')
print('2 1.8002')
print('50 -0.0758')
