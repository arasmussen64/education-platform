import numpy as np

rng = np.random.default_rng(11)
sample = rng.exponential(10, size=40)


def bootstrap_interval(rng, sample, statistic, draws=2000):
    values = np.array([statistic(rng.choice(sample, size=len(sample))) for _ in range(draws)])
    low, high = np.percentile(values, [2.5, 97.5])
    return round(float(low), 2), round(float(high), 2)


print(round(float(np.median(sample)), 2), bootstrap_interval(rng, sample, np.median))
print(round(float(sample.mean()), 2), bootstrap_interval(rng, sample, np.mean))
