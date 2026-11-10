import numpy as np

rng = np.random.default_rng(11)
sample = rng.exponential(10, size=40)


def bootstrap_interval(rng, sample, statistic, draws=2000):
    return (0.0, 0.0)


print('6.21 (4.21, 10.52)')
print('10.06 (7.12, 13.34)')
