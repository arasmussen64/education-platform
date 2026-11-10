import numpy as np


def coin_likelihood(ps, heads, flips):
    return ps**heads * (1 - ps) ** (flips - heads)


def normal_log_likelihood(mus, x, sigma):
    return np.array([-((x - mu) ** 2).sum() / (2 * sigma**2) for mu in mus])


ps = np.linspace(0.01, 0.99, 99)
print("coin", round(float(ps[coin_likelihood(ps, 6, 8).argmax()]), 2))
rng = np.random.default_rng(6)
x = rng.normal(170, 10, size=1000)
mus = np.linspace(165, 175, 101)
print("normal", round(float(mus[normal_log_likelihood(mus, x, 10).argmax()]), 1))
