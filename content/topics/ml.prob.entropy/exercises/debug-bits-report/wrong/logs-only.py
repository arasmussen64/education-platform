import numpy as np


def entropy(p):
    p = np.asarray(p)
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum()) + 0.0


def cross_entropy(p, q):
    p, q = np.asarray(p), np.asarray(q)
    keep = p > 0
    return float(-(p[keep] * np.log2(q[keep])).sum())


def kl(p, q):
    return entropy(p) - cross_entropy(p, q)


print("fair coin", entropy([0.5, 0.5]), "bits")
print("fair die", round(entropy([1 / 6] * 6), 3), "bits")
truth, belief = [0.7, 0.2, 0.1], [0.5, 0.3, 0.2]
print("kl", round(kl(truth, belief), 3))
