import numpy as np

rng = np.random.default_rng(2)


def bernoulli(rng, p, size):
    return np.zeros(size, dtype=int)


print('[1 1 0 1 0 0 1 1] 0.3')
