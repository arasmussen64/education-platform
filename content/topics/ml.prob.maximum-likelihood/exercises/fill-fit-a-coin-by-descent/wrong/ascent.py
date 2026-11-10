import numpy as np


def negative_log_likelihood(p, heads, flips):
    return -(heads * np.log(p) + (flips - heads) * np.log(1 - p))


def fit_coin(heads, flips, rate=0.01, steps=500):
    p = 0.5
    for step in range(steps):
        slope = -heads / p + (flips - heads) / (1 - p)
        p = p + rate * slope
    return p


print(round(negative_log_likelihood(0.75, 6, 8), 4), round(negative_log_likelihood(0.5, 6, 8), 4))
print(round(fit_coin(6, 8), 4), round(fit_coin(3, 10), 4), round(fit_coin(50, 100), 4))
