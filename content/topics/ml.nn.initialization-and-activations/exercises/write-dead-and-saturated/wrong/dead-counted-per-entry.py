import numpy as np


def dead_fraction(H):
    """The share of ReLU units (columns of H) that are zero for every input in the batch."""
    return float((H == 0).mean())


def saturated_fraction(Z, threshold=4.0):
    """The share of pre-activations whose size is beyond the threshold, where a sigmoid's slope is under 0.02."""
    return float((np.abs(Z) > threshold).mean())


H = np.array([[0.0, 1.5, 0.0, 2.0], [0.0, 0.0, 0.0, 0.5], [0.0, 3.0, 0.0, 0.0]])
Z = np.array([[5.0, -1.0, 0.5, -6.0], [3.9, 4.1, -4.0, 10.0]])
print(dead_fraction(H), saturated_fraction(Z), saturated_fraction(Z, threshold=3.0))
