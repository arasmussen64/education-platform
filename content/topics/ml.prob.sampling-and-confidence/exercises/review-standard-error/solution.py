import numpy as np

scores = np.array([72.0, 85.0, 90.0, 66.0, 78.0, 81.0, 95.0, 70.0, 88.0, 75.0])


def standard_error(sample):
    return float(sample.std(ddof=1) / np.sqrt(len(sample)))


print(round(standard_error(scores), 3))
print(round(standard_error(np.tile(scores, 4)), 3))
