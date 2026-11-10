import math

import numpy as np


def binomial_pmf(k, n, p):
    return math.comb(n, k) * p**k * (1 - p) ** (n - k)


def empirical_pmf(sample, n):
    counts = np.bincount(sample, minlength=n + 1)
    return counts / len(sample)


def largest_gap(sample, n, p):
    simulated = empirical_pmf(sample, n)
    exact = np.array([binomial_pmf(k, n, p) for k in range(n + 1)])
    return float(np.abs(simulated - exact).max())


def within(sample, center, spread):
    return [float(np.mean(np.abs(sample - center) < width * spread)) for width in (1, 2, 3)]


rng = np.random.default_rng(1)
heads = rng.binomial(10, 0.3, size=100000)
print("pmf", np.round(empirical_pmf(heads, 10)[:4], 3))
print("largest gap below 0.003", largest_gap(heads, 10, 0.3) < 0.003)
heights = rng.normal(170, 10, size=100000)
print("within 1, 2, 3 spreads", np.round(within(heights, 170, 10), 3))
