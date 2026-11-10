import numpy as np


def mle_coin(heads, flips):
    ps = np.linspace(0.001, 0.999, 999)
    return float(ps[(heads * np.log(ps)).argmax()])


print(mle_coin(6, 8), mle_coin(3, 10), mle_coin(1, 1000))
