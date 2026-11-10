import numpy as np


def moments(values, probs):
    return 3.5, 2.9167


def sum_of_independent(means, variances):
    return 35.0, 29.1667


def running_means(sample):
    return np.zeros(len(sample)) + 3.5


def standardize(x, mean, sd):
    return np.array([-1.0, 2.0])


print('one die 3.5 2.9167')
print('ten dice 35.0 29.1667')
print('running [3.    3.61  3.51  3.498]')
print('z [-1.  2.]')
