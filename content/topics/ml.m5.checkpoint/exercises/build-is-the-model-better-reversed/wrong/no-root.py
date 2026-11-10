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


def choose_threshold(y_val, score_val):
    thresholds = np.arange(0.0, 2.01, 0.05)
    accuracies = [((score_val > t).astype(int) == y_val).mean() for t in thresholds]
    return float(round(thresholds[int(np.argmax(accuracies))], 2))


def report(rng, y, score_a, score_b, threshold_a, threshold_b):
    pred_a = (score_a > threshold_a).astype(int)
    pred_b = (score_b > threshold_b).astype(int)
    for name, pred in (("A", pred_a), ("B", pred_b)):
        counts = confusion(y, pred)
        print(name, counts, np.round(metrics(*counts), 3))
    correct_a = (pred_a == y).astype(int)
    correct_b = (pred_b == y).astype(int)
    print("interval A", np.round(accuracy_interval(correct_a), 3))
    print("interval B", np.round(accuracy_interval(correct_b), 3))
    mean, low, high = paired_bootstrap(rng, correct_a, correct_b)
    print("A minus B", round(mean, 3), np.round([low, high], 3))
    if low > 0:
        print("verdict: A is better")
    elif high < 0:
        print("verdict: B is better")
    else:
        print("verdict: not established")


rng = np.random.default_rng(23)
n = 200
y = (rng.random(n) < 0.3).astype(int)
score_a = y * 1.3 + rng.normal(0, 1, size=n)
score_b = y * 2.2 + rng.normal(0, 1, size=n)
y_val = (rng.random(n) < 0.3).astype(int)
score_a_val = y_val * 1.3 + rng.normal(0, 1, size=n)
score_b_val = y_val * 2.2 + rng.normal(0, 1, size=n)
threshold_a = choose_threshold(y_val, score_a_val)
threshold_b = choose_threshold(y_val, score_b_val)
print("thresholds", threshold_a, threshold_b)
report(rng, y, score_a, score_b, threshold_a, threshold_b)
