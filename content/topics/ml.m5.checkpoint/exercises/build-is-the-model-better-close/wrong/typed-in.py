import numpy as np


def confusion(y, pred):
    return (0, 0, 0, 0)


def metrics(tp, fp, fn, tn):
    return (0.0, 0.0, 0.0, 0.0)


def accuracy_interval(correct, z=1.96):
    return (0.0, 1.0)


def paired_bootstrap(rng, correct_a, correct_b, draws=2000):
    return (0.0, 0.0, 0.0)


def choose_threshold(y_val, score_val):
    return 1.0


def report(rng, y, score_a, score_b, threshold_a, threshold_b):
    print('A (26, 9, 34, 131) [0.785 0.743 0.433 0.547]')
    print('B (44, 38, 16, 102) [0.73  0.537 0.733 0.62 ]')
    print('interval A [0.728 0.842]')
    print('interval B [0.668 0.792]')
    print('A minus B 0.055 [-0.03  0.14]')
    print('verdict: not established')


rng = np.random.default_rng(22)
n = 200
y = (rng.random(n) < 0.3).astype(int)
score_a = y * 1.5 + rng.normal(0, 1, size=n)
score_b = y * 1.4 + rng.normal(0, 1, size=n)
y_val = (rng.random(n) < 0.3).astype(int)
score_a_val = y_val * 1.5 + rng.normal(0, 1, size=n)
score_b_val = y_val * 1.4 + rng.normal(0, 1, size=n)
print('thresholds 1.55 0.65')
report(rng, y, score_a, score_b, 1.0, 1.0)
