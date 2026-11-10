import numpy as np


def clip_gradients(grads, max_norm):
    """Scale every gradient by the same factor so that their norm, all together, is at most max_norm; unchanged if it already is."""
    norm = float(np.sqrt(sum(float((grad ** 2).sum()) for grad in grads)))
    if norm > max_norm:
        return [grad * (max_norm / norm) for grad in grads]
    return grads


grads = [np.array([6.0, 0.0]), np.array([[8.0]])]
print([grad.tolist() for grad in clip_gradients(grads, 5.0)])
print([grad.tolist() for grad in clip_gradients(grads, 20.0)])
