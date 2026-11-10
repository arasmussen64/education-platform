import numpy as np


def expectation(values, probs):
    return (values * ...).sum()


def variance(values, probs):
    mu = expectation(values, probs)
    return ((values - mu) ** ... * probs).sum()


die = np.arange(1, 7)
fair = np.full(6, 1 / 6)
print(expectation(die, fair), round(float(variance(die, fair)), 4))
coin = np.array([0.0, 1.0])
print(expectation(coin, np.array([0.7, 0.3])), round(float(variance(coin, np.array([0.7, 0.3]))), 4))
loaded = np.array([0.5, 0.1, 0.1, 0.1, 0.1, 0.1])
print(round(float(expectation(die, loaded)), 4), round(float(variance(die, loaded)), 4))
