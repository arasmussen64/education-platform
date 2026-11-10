import numpy as np


def softmax(scores):
    e = np.exp(scores - scores.max())
    return e / e.sum()


print(np.round(softmax(np.array([2.0, 1.0, 0.1])), 3))
print(softmax(np.array([1000.0, 1000.0])))
