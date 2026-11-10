import numpy as np


def log_likelihood_coin(p, heads, flips):
    return heads * np.log(p) + (flips - heads) * np.log(1 - p)


def mle_coin(heads, flips):
    ps = np.linspace(0.001, 0.999, 999)
    return float(ps[log_likelihood_coin(ps, heads, flips).argmax()])


def nll_bernoulli(p_hat, y):
    return float(-np.sum(y * np.log(p_hat) + (1 - y) * np.log(1 - p_hat)))


def nll_normal(x, mu, sigma):
    return float(((x - mu) ** 2).sum() / 2)


print("coin", mle_coin(6, 8), mle_coin(3, 10))
y = np.array([1.0, 0.0, 1.0, 1.0])
p_hat = np.array([0.9, 0.2, 0.7, 0.6])
print("labels", round(nll_bernoulli(p_hat, y), 4), round(float(-np.log(np.prod(np.where(y == 1, p_hat, 1 - p_hat)))), 4))
x = np.array([168.0, 171.0, 174.0, 167.0, 170.0])
print("normal", [round(nll_normal(x, mu, 3.0), 3) for mu in (168.0, 170.0, 172.0)])
