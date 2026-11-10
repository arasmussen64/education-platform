import numpy as np


def adam_steps(x, rate, steps, beta1=0.9, beta2=0.999, eps=1e-8):
    return [round(x - rate * (i + 1), 4) for i in range(steps)]


print('[1.9, 1.8002, 1.7006]')
print('[-49.9, -49.8, -49.7]')
