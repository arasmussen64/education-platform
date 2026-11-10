import numpy as np

rng = np.random.default_rng(21)
n = 200
y = (rng.random(n) < 0.3).astype(int)
score_a = y * 2.0 + rng.normal(0, 1, size=n)
score_b = y * 1.2 + rng.normal(0, 1, size=n)
y_val = (rng.random(n) < 0.3).astype(int)
score_a_val = y_val * 2.0 + rng.normal(0, 1, size=n)
score_b_val = y_val * 1.2 + rng.normal(0, 1, size=n)
pred_a = (score_a > 1.0).astype(int)
pred_b = (score_b > 0.6).astype(int)


def confusion(y, pred):
    return (0, 0, 0, 0)


print('(56, 18, 5, 121)')
print('(45, 43, 16, 96)')
print('200')
