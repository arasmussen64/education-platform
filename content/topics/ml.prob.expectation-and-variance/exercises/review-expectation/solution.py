import numpy as np

values = np.array([0.0, 10.0, 100.0])
probs = np.array([0.89, 0.1, 0.01])


def expectation(values, probs):
    return float((values * probs).sum())


print(expectation(values, probs))
print(expectation(np.arange(1, 7), np.full(6, 1 / 6)))
