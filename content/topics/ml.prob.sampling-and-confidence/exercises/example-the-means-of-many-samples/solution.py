import numpy as np

rng = np.random.default_rng(8)
population = rng.exponential(10, size=200000)
print(round(float(population.mean()), 2), round(float(population.std()), 2), round(float(np.median(population)), 2))

for n in (2, 10, 50):
    means = rng.exponential(10, size=(20000, n)).mean(axis=1)
    print(n, round(float(means.mean()), 2), round(float(means.std()), 2), round(10 / np.sqrt(n), 2))

means = rng.exponential(10, size=(20000, 50)).mean(axis=1)
counts, edges = np.histogram(means, bins=np.arange(5, 15.5, 1.0))
for count, left in zip(counts, edges[:-1]):
    print(f"{left:5.1f} {'#' * round(count / 200)}")

sample = rng.exponential(10, size=50)
mean = sample.mean()
se = sample.std(ddof=1) / np.sqrt(len(sample))
print(round(float(mean), 2), round(float(se), 2), round(float(mean - 1.96 * se), 2), round(float(mean + 1.96 * se), 2))

covered = 0
for trial in range(2000):
    s = rng.exponential(10, size=50)
    half = 1.96 * s.std(ddof=1) / np.sqrt(50)
    covered += abs(s.mean() - 10) < half
print(covered / 2000)

medians = np.array([np.median(rng.choice(sample, size=50)) for _ in range(2000)])
print(round(float(np.median(sample)), 2), np.round(np.percentile(medians, [2.5, 97.5]), 2))
