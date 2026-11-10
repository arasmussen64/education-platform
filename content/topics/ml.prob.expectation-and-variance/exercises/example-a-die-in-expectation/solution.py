import numpy as np

faces = np.arange(1, 7)
p = np.full(6, 1 / 6)
mean = (faces * p).sum()
variance = ((faces - mean) ** 2 * p).sum()
print(mean, round(float(variance), 4), round(float(np.sqrt(variance)), 3))

rng = np.random.default_rng(2)
rolls = rng.integers(1, 7, size=100000)
print(round(float(rolls.mean()), 3), round(float(rolls.var()), 3))
for n in (10, 100, 1000, 10000, 100000):
    print(n, round(float(rolls[:n].mean()), 3))

two_dice = rolls[:50000] + rolls[50000:]
print(round(float(two_dice.mean()), 3), round(float(two_dice.var()), 3))
one_die_doubled = 2 * rolls
print(round(float(one_die_doubled.mean()), 3), round(float(one_die_doubled.var()), 3))

heights = rng.normal(170, 10, size=5)
print(np.round(heights, 1))
print(np.round((heights - 170) / 10, 2))
