import numpy as np


def standard_error(sample):
    return float(sample.std(ddof=1) / len(sample))


def confidence_interval(sample, z=1.96):
    half = z * standard_error(sample)
    return float(sample.mean() - half), float(sample.mean() + half)


def coverage(rng, draw, truth, n, trials):
    hits = 0
    for trial in range(trials):
        low, high = confidence_interval(draw(rng, n))
        hits += low < truth < high
    return hits / trials


def bootstrap_interval(rng, sample, statistic, draws=2000):
    values = np.array([statistic(rng.choice(sample, size=len(sample))) for _ in range(draws)])
    low, high = np.percentile(values, [2.5, 97.5])
    return float(low), float(high)


rng = np.random.default_rng(8)
sample = rng.exponential(10, size=50)
print("standard error", round(standard_error(sample), 3))
print("interval", np.round(confidence_interval(sample), 2))
print("coverage", coverage(rng, lambda rng, n: rng.exponential(10, size=n), 10, 50, 2000))
print("median", round(float(np.median(sample)), 2), np.round(bootstrap_interval(rng, sample, np.median), 2))
