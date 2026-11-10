import numpy as np


def mle_coin(heads, flips):
    ps = np.linspace(0.001, 0.999, 999)
    log_likelihood = heads * np.log(ps) + (flips - heads) * np.log(1 - ps)
    return float(ps[log_likelihood.argmax()])


print(mle_coin(6, 8), mle_coin(3, 10), mle_coin(1, 1000))
