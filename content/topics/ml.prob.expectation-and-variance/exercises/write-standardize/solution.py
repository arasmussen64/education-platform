import numpy as np


def standardize(x, mean, sd):
    return (x - mean) / sd


print(standardize(75, 60, 10), standardize(80, 70, 20))
print(np.round(standardize(np.array([150.0, 170.0, 195.0]), 170, 10), 1))
