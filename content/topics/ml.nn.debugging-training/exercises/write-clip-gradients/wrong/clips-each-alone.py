import numpy as np


def gradient_norm(grads):
    """The length of all the gradients taken together, as one vector."""
    return float(np.sqrt(sum(float((grad ** 2).sum()) for grad in grads)))


def clip_gradients(grads, max_norm):
    """Scale every gradient by the same factor so their norm is at most max_norm; leave them alone if it already is."""
    return [grad * (max_norm / gradient_norm([grad])) if gradient_norm([grad]) > max_norm else grad for grad in grads]


grads = [np.array([[3.0, 0.0], [0.0, 0.0]]), np.array([4.0]), np.array([12.0])]
print(gradient_norm(grads))
clipped = clip_gradients(grads, 6.5)
print([grad.tolist() for grad in clipped], gradient_norm(clipped))
print(clip_gradients(grads, 100.0) is grads)
