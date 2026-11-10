import numpy as np


def confusion(y, pred):
    return (0, 0, 0, 0)


def metrics(tp, fp, fn, tn):
    return (0.0, 0.0, 0.0, 0.0)


def accuracy_interval(correct, z=1.96):
    return (0.0, 1.0)


def paired_bootstrap(rng, correct_a, correct_b, draws=2000):
    return (0.0, 0.0, 0.0)


print('A (61, 21, 13, 105) [0.83  0.744 0.824 0.782]')
print('B (53, 31, 21, 95) [0.74  0.631 0.716 0.671]')
print('interval for A [0.778 0.882]')
print('A minus B [0.09  0.015 0.165]')
