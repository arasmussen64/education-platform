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


print(surprise(0.5), surprise(1 / 8), surprise(1.0), surprise(1 / 1024))
print(entropy([0.5, 0.5]), round(entropy([0.9, 0.1]), 3), round(entropy([1 / 6] * 6), 3), entropy([1.0, 0.0]))

weather = [0.7, 0.2, 0.1]
print(round(entropy(weather), 3))
beliefs = {
    "right": [0.7, 0.2, 0.1],
    "hedged": [0.5, 0.3, 0.2],
    "uniform": [1 / 3, 1 / 3, 1 / 3],
    "upside down": [0.1, 0.2, 0.7],
}
for name, q in beliefs.items():
    ce = cross_entropy(weather, q)
    print(name, round(ce, 3), round(ce - entropy(weather), 3))

labels = np.array([1.0, 0.0, 1.0, 1.0])
p_hat = np.array([0.9, 0.2, 0.7, 0.6])
bits = [cross_entropy([y, 1 - y], [p, 1 - p]) for y, p in zip(labels, p_hat)]
print(np.round(bits, 3), round(float(np.mean(bits)), 3), round(float(np.mean(bits) * np.log(2)), 3))
