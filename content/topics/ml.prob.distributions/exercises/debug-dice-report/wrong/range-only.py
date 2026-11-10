import math

import numpy as np


def roll(rng, size):
    return rng.integers(1, 7, size=size)


def sixes_pmf(k):
    return math.comb(4, k) * (1 / 6) ** k * (5 / 6) ** k


rng = np.random.default_rng(5)
rolls = roll(rng, 60000)
counts = np.bincount(rolls, minlength=7)[1:]
print("faces", np.round(counts / len(rolls), 3))

sixes = rng.binomial(4, 1 / 6, size=60000)
for k in range(5):
    print(k, round(float(np.mean(sixes == k)), 3), round(sixes_pmf(k), 3))
