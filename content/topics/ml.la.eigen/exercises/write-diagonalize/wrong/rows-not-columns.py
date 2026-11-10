import numpy as np

A = np.array([[4.0, 1.0], [2.0, 3.0]])


def diagonalize(A):
    values, vectors = np.linalg.eig(A)
    return vectors.T, np.diag(values)


def power(A, k):
    P, D = diagonalize(A)
    return P @ np.linalg.matrix_power(D, k) @ np.linalg.inv(P)


P, D = diagonalize(A)
print(np.allclose(P @ D @ np.linalg.inv(P), A))
print(np.allclose(power(A, 4), np.linalg.matrix_power(A, 4)))
