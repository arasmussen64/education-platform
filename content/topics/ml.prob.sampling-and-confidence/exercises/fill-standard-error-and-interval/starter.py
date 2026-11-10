import numpy as np


def standard_error(sample):
    return sample.std(ddof=1) / np.sqrt(...)


def confidence_interval(sample, z=1.96):
    mean = sample.mean()
    half = ... * standard_error(sample)
    return round(float(mean - half), 2), round(float(mean + half), 2)


scores = np.array([72.0, 85.0, 90.0, 66.0, 78.0, 81.0, 95.0, 70.0, 88.0, 75.0])
print(round(float(standard_error(scores)), 3))
print(confidence_interval(scores))
print(confidence_interval(np.tile(scores, 4)))
