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


def paired_bootstrap(rng, correct_a, correct_b, draws=2000):
    diff = correct_a - correct_b
    means = np.array([rng.choice(diff, size=len(diff)).mean() for _ in range(draws)])
    low, high = np.percentile(means, [2.5, 97.5])
    return float(diff.mean()), float(low), float(high)


correct_a = (pred_a == y).astype(int)
correct_b = (pred_b == y).astype(int)
mean, low, high = paired_bootstrap(rng, correct_a, correct_b)
print(round(mean, 3), round(low, 3), round(high, 3))
print(low > 0)
