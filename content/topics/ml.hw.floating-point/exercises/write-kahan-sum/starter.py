import numpy as np


def plain_sum(values):
    total = np.float32(0)
    for value in values:
        total += np.float32(value)
    return float(total)


tenths = [0.1] * 100_000
print("plain:", plain_sum(tenths))
