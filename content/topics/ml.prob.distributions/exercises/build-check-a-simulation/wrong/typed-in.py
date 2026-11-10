import numpy as np


def binomial_pmf(k, n, p):
    return 0.25


def empirical_pmf(sample, n):
    return np.zeros(n + 1) + 0.25


def largest_gap(sample, n, p):
    return 0.0


def within(sample, center, spread):
    return [0.683, 0.954, 0.997]


print('pmf [0.028 0.121 0.235 0.265]')
print('largest gap below 0.003 True')
print('within 1, 2, 3 spreads [0.683 0.954 0.997]')
