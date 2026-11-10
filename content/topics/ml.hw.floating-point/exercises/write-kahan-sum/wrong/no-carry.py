import numpy as np


def kahan_sum(values):
    """Sum values in float32 while carrying the rounding error forward, so it doesn't accumulate."""
    total = np.float32(0)
    carry = np.float32(0)
    for value in values:
        adjusted = np.float32(value) - carry
        new_total = total + adjusted
        total = new_total
    return float(total)


def plain_sum(values):
    total = np.float32(0)
    for value in values:
        total += np.float32(value)
    return float(total)


tenths = [0.1] * 100_000
print("plain:", plain_sum(tenths))
print("kahan:", kahan_sum(tenths))
