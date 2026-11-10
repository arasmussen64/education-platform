import numpy as np


def normalize(values):
    low = values.min()
    high = values.max()
    return (values - low) / (high - low)


print(normalize(np.array([2.0, 4.0, 6.0, 10.0])))
