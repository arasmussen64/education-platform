import numpy as np


def report(A, values, vectors):
    for i in range(len(values)):
        v = vectors[:, i]
        ok = bool(np.allclose(A @ v, values[0] * v))
        print("eigenvalue", round(float(values[0]), 6), "check", ok)


A = np.array([[2.0, 1.0], [0.0, 3.0]])
values = np.array([2.0, 3.0])
vectors = np.array([[1.0, 1.0], [0.0, 1.0]])
report(A, values, vectors)
