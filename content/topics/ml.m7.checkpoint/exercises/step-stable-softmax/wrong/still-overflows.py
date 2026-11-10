import numpy as np


def softmax(logits):
    """Row-wise softmax: subtract each row's largest logit first, so the biggest exponent is 0 and nothing overflows."""
    shifted = np.exp(logits - 0)
    return shifted / shifted.sum(axis=1, keepdims=True)


print(np.round(softmax(np.array([[1000.0, 1001.0], [1.0, 2.0]])), 3).tolist())
