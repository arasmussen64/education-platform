import numpy as np

pred = np.array([2.5, 0.0, 2.1, 7.8])
target = np.array([3.0, -0.5, 2.0, 8.0])


def mse(pred, target):
    return float(np.mean(np.abs(pred - target)))


print(round(mse(pred, target), 4))
