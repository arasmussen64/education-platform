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


def accuracy_interval(correct, z=1.96):
    p = correct.mean()
    se = np.sqrt(p * (1 - p) / ...)
    return float(p - ... * se), float(p + ... * se)


correct_a = (pred_a == y).astype(int)
correct_b = (pred_b == y).astype(int)
print(round(float(correct_a.mean()), 3), np.round(accuracy_interval(correct_a), 3))
print(round(float(correct_b.mean()), 3), np.round(accuracy_interval(correct_b), 3))
