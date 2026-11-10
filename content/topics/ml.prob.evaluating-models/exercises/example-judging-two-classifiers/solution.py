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
    tp, fp, fn, tn = confusion(y, pred)
    print(name, (tp, fp, fn, tn), np.round(metrics(tp, fp, fn, tn), 3))
print("always no", round(float((y == 0).mean()), 3))

correct = (pred_a == y).astype(int)
accuracy = correct.mean()
se = np.sqrt(accuracy * (1 - accuracy) / n)
print(round(float(accuracy), 3), round(float(se), 3), np.round([accuracy - 1.96 * se, accuracy + 1.96 * se], 3))

thresholds = np.arange(0.0, 2.01, 0.05)
best_val = thresholds[np.argmax([((score_a_val > t).astype(int) == y_val).mean() for t in thresholds])]
best_test = thresholds[np.argmax([((score_a > t).astype(int) == y).mean() for t in thresholds])]
print(round(float(best_val), 2), round(float(((score_a > best_val).astype(int) == y).mean()), 3))
print(round(float(best_test), 2), round(float(((score_a > best_test).astype(int) == y).mean()), 3))

diff = correct - (pred_b == y).astype(int)
boot = np.array([rng.choice(diff, size=n).mean() for _ in range(2000)])
print(round(float(diff.mean()), 3), np.round(np.percentile(boot, [2.5, 97.5]), 3))
