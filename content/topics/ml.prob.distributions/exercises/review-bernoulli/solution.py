import numpy as np

rng = np.random.default_rng(2)


def bernoulli(rng, p, size):
    return (rng.random(size) < p).astype(int)


draws = bernoulli(rng, 0.3, 100000)
print(draws[:8], round(float(draws.mean()), 2))
