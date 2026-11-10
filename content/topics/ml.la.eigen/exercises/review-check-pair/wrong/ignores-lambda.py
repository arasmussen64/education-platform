import numpy as np

A = np.array([[2.0, 1.0], [1.0, 2.0]])


def is_eigenpair(A, v, lam):
    return bool(np.allclose(A @ v, v))


print(is_eigenpair(A, np.array([1.0, 1.0]), 3.0))
print(is_eigenpair(A, np.array([1.0, -1.0]), 1.0))
print(is_eigenpair(A, np.array([1.0, 0.0]), 2.0))
