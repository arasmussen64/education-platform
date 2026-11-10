import numpy as np


def entropy(p):
    p = np.asarray(p)
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum()) + 0.0


print(entropy([0.5, 0.5]), round(entropy([0.9, 0.1]), 3), entropy([1 / 4] * 4), entropy([1.0, 0.0]))
