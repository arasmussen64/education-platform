import numpy as np


def surprise(p):
    return -np.log2(p) + 0.0


def entropy(p):
    p = np.asarray(p)
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum()) + 0.0


def cross_entropy(p, q):
    p, q = np.asarray(p), np.asarray(q)
    keep = p > 0
    return float(-(p[keep] * np.log2(q[keep])).sum())


def kl(p, q):
    p, q = np.asarray(p), np.asarray(q)
    keep = p > 0
    return float((p[keep] * np.log2(p[keep] / q[keep])).sum())


weather = [0.7, 0.2, 0.1]
for q in ([0.7, 0.2, 0.1], [0.5, 0.3, 0.2], [1 / 3, 1 / 3, 1 / 3]):
    print(round(kl(weather, q), 3), round(cross_entropy(weather, q) - entropy(weather), 3))
print(round(kl([0.9, 0.1], [0.5, 0.5]), 3), round(kl([0.5, 0.5], [0.9, 0.1]), 3))
