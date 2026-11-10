import numpy as np


def d_relu(x):
    return np.where(x > 0, 1.0, 0.0)


print(d_relu(np.array([-3.0, 0.5, 2.0])))
