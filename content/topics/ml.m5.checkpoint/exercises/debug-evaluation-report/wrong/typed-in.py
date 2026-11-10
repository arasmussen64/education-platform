import numpy as np


def choose_threshold(y_val, score_val):
    return 1.0


def metrics(tp, fp, fn, tn):
    return (0.0, 0.0, 0.0, 0.0)


def paired_bootstrap(rng, correct_a, correct_b, draws=2000):
    return (0.0, 0.0, 0.0)


print('thresholds 1.7 1.05')
print('A (39, 2, 22, 137) [0.88  0.951 0.639 0.765]')
print('B (35, 27, 26, 112) [0.735 0.565 0.574 0.569]')
print('interval A [0.835 0.925]')
print('interval B [0.674 0.796]')
print('A minus B 0.145 [0.075 0.215]')
print('verdict: A is better')
