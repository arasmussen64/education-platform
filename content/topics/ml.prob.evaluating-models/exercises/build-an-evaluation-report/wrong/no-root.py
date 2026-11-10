import numpy as np


def confusion(y, pred):
    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    return tp, fp, fn, tn


def metrics(tp, fp, fn, tn):
    accuracy = (tp + tn) / (tp + fp + fn + tn)
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * precision * recall / (precision + recall)
    return accuracy, precision, recall, f1


def accuracy_interval(correct, z=1.96):
    p = correct.mean()
    se = p * (1 - p) / len(correct)
    return float(p - z * se), float(p + z * se)


def paired_bootstrap(rng, correct_a, correct_b, draws=2000):
    diff = correct_a - correct_b
    means = np.array([rng.choice(diff, size=len(diff)).mean() for _ in range(draws)])
    low, high = np.percentile(means, [2.5, 97.5])
    return float(diff.mean()), float(low), float(high)


rng = np.random.default_rng(12)
n = 200
y = (rng.random(n) < 0.3).astype(int)
score_a = y * 2.0 + rng.normal(0, 1, size=n)
score_b = y * 1.2 + rng.normal(0, 1, size=n)
y_val = (rng.random(n) < 0.3).astype(int)
score_a_val = y_val * 2.0 + rng.normal(0, 1, size=n)

pred_a = (score_a > 1.0).astype(int)
pred_b = (score_b > 0.6).astype(int)
for name, pred in (("A", pred_a), ("B", pred_b)):
    print(name, confusion(y, pred), np.round(metrics(*confusion(y, pred)), 3))
correct_a = (pred_a == y).astype(int)
correct_b = (pred_b == y).astype(int)
print("interval for A", np.round(accuracy_interval(correct_a), 3))
print("A minus B", np.round(paired_bootstrap(rng, correct_a, correct_b), 3))
