import math

import numpy as np

rng = np.random.default_rng(1)

flips = rng.random(10) < 0.3
print(flips.astype(int), flips.sum())

heads = rng.binomial(10, 0.3, size=100000)
counts = np.bincount(heads, minlength=11)
print(counts[:5])
for k in range(5):
    simulated = counts[k] / len(heads)
    exact = math.comb(10, k) * 0.3**k * 0.7 ** (10 - k)
    print(k, round(float(simulated), 3), round(exact, 3), "#" * round(exact * 50))

u = rng.uniform(0, 1, size=100000)
print(round(float(np.mean(u < 0.25)), 3), round(float(np.mean(u == 0.25)), 3))

heights = rng.normal(170, 10, size=100000)
print(round(float(heights.mean()), 1), round(float(heights.std()), 1))
for width in (1, 2, 3):
    inside = np.mean(np.abs(heights - 170) < width * 10)
    print(width, round(float(inside), 3))
