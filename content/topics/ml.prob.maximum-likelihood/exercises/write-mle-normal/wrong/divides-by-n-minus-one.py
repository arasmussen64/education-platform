import numpy as np

rng = np.random.default_rng(6)
x = rng.normal(170, 10, size=1000)


def mle_normal(x):
    mu = x.mean()
    sigma = np.sqrt(((x - mu) ** 2).sum() / (len(x) - 1))
    return float(mu), float(sigma)


mu, sigma = mle_normal(x)
print(round(mu, 2), round(sigma, 2))
print(round(mu, 2) == round(float(x.mean()), 2), round(sigma, 2) == round(float(x.std()), 2))
print(mle_normal(np.array([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])))
