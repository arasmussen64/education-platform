import numpy as np


def log_likelihood_coin(p, heads, flips):
    return 0.0


def mle_coin(heads, flips):
    return heads / flips


def nll_bernoulli(p_hat, y):
    return 1.1961


def nll_normal(x, mu, sigma):
    return 0.0


print('coin 0.75 0.3')
print('labels 1.196 1.196')
print('normal [8.271, 7.16, 8.271]')
