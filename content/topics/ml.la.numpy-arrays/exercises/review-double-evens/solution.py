import numpy as np

values = np.array([1, 2, 3, 4, 5, 6])


def double_evens(values):
    return values[values % 2 == 0] * 2


print(double_evens(values))
