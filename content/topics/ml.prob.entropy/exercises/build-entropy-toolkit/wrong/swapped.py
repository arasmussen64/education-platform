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
    return float(-(q[keep] * np.log2(p[keep])).sum())


def kl(p, q):
    return cross_entropy(p, q) - entropy(p)


def loss_in_nats(labels, p_hat):
    picked = np.where(labels == 1, p_hat, 1 - p_hat)
    return float(np.mean(-np.log(picked)))


truth = [0.7, 0.2, 0.1]
print("entropy", round(entropy(truth), 3), "uniform of 8", entropy([1 / 8] * 8))
for q in ([0.7, 0.2, 0.1], [0.5, 0.3, 0.2], [1 / 3, 1 / 3, 1 / 3]):
    print("cross-entropy", round(cross_entropy(truth, q), 3), "kl", round(kl(truth, q), 3))
print("kl both ways", round(kl([0.9, 0.1], [0.5, 0.5]), 3), round(kl([0.5, 0.5], [0.9, 0.1]), 3))
labels = np.array([1.0, 0.0, 1.0, 1.0])
p_hat = np.array([0.9, 0.2, 0.7, 0.6])
print("loss", round(loss_in_nats(labels, p_hat), 3))
