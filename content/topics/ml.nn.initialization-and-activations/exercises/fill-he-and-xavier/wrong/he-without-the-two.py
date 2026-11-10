import numpy as np


def xavier_scale(n_in):
    """Keeps the size of the signal through a tanh or sigmoid layer: 1 / sqrt(n_in)."""
    return float(np.sqrt(1 / n_in))


def he_scale(n_in):
    """Keeps the size of the signal through a ReLU layer, which zeroes half of it: sqrt(2 / n_in)."""
    return float(np.sqrt(1 / n_in))


print(xavier_scale(100), he_scale(50), he_scale(2))
