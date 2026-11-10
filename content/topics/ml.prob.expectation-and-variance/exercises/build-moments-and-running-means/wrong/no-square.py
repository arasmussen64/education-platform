import math

import numpy as np


def moments(values, probs):
    mean = float((values * probs).sum())
    variance = float((np.abs(values - mean) * probs).sum())
    return mean, variance


def sum_of_independent(means, variances):
    return float(sum(means)), float(sum(variances))


def running_means(sample):
    return np.cumsum(sample) / np.arange(1, len(sample) + 1)


def standardize(x, mean, sd):
    return (x - mean) / sd


die = np.arange(1, 7)
fair = np.full(6, 1 / 6)
mean, variance = moments(die, fair)
print("one die", mean, round(variance, 4))
total_mean, total_variance = sum_of_independent([mean] * 10, [variance] * 10)
print("ten dice", total_mean, round(total_variance, 4))
rng = np.random.default_rng(2)
means = running_means(rng.integers(1, 7, size=10000))
print("running", np.round(means[[9, 99, 999, 9999]], 3))
print("z", standardize(np.array([160.0, 190.0]), 170, 10))
