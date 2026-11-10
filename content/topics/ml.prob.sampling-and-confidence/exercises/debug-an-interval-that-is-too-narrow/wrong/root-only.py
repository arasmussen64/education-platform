import numpy as np


def interval(sample, z=1.96):
    se = sample.std(ddof=1) / np.sqrt(len(sample))
    return sample.mean() - se, sample.mean() + se


rng = np.random.default_rng(3)
sample = rng.normal(100, 15, size=36)
low, high = interval(sample)
print("interval", round(float(low), 1), round(float(high), 1))

hits = 0
for trial in range(1000):
    low, high = interval(rng.normal(100, 15, size=36))
    hits += low < 100 < high
print("coverage", hits / 1000)
