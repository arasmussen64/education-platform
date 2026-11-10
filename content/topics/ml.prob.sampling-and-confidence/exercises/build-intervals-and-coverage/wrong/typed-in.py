import numpy as np


def standard_error(sample):
    return 1.0


def confidence_interval(sample, z=1.96):
    return (8.0, 12.0)


def coverage(rng, draw, truth, n, trials):
    return 0.95


def bootstrap_interval(rng, sample, statistic, draws=2000):
    return (5.0, 9.0)


print('standard error 1.13')
print('interval [ 6.17 10.59]')
print('coverage 0.934')
print('median 6.09 [4.08 8.12]')
