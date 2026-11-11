import numpy as np


def after_years(T, start, years):
    return np.linalg.matrix_power(T, years) @ start


def steady_state(T):
    values, vectors = np.linalg.eig(T)
    i = int(np.argmin(np.abs(values - 1)))
    # np.real keeps the real part of each entry. It changes nothing for these
    # matrices, whose eigenvalues are real, so vectors[:, i] alone passes too;
    # it's a guard for a matrix that makes eig return complex numbers.
    s = np.real(vectors[:, i])
    return s / s.sum()


T = np.array([[0.9, 0.2], [0.1, 0.8]])
start = np.array([1000.0, 0.0])
print(np.round(after_years(T, start, 1), 1))
print(np.round(after_years(T, start, 10), 1))
print(np.round(steady_state(T), 3))
