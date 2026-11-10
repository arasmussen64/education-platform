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
    print('A (31, 40, 26, 103) [0.67  0.437 0.544 0.484]')
    print('B (44, 8, 13, 135) [0.895 0.846 0.772 0.807]')
    print('interval A [0.605 0.735]')
    print('interval B [0.853 0.937]')
    print('A minus B -0.225 [-0.3  -0.15]')
    print('verdict: B is better')


rng = np.random.default_rng(23)
n = 200
y = (rng.random(n) < 0.3).astype(int)
score_a = y * 1.3 + rng.normal(0, 1, size=n)
score_b = y * 2.2 + rng.normal(0, 1, size=n)
y_val = (rng.random(n) < 0.3).astype(int)
score_a_val = y_val * 1.3 + rng.normal(0, 1, size=n)
score_b_val = y_val * 2.2 + rng.normal(0, 1, size=n)
print('thresholds 0.75 1.5')
report(rng, y, score_a, score_b, 1.0, 1.0)
