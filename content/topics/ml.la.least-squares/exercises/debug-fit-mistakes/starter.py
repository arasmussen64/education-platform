import numpy as np


def fit_line(xs, ys):
    A = np.column_stack([np.ones(len(xs)), xs])
    coef = np.linalg.solve(A @ A.T, A.T @ ys)
    slope, intercept = coef
    return slope, intercept


xs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
ys = np.array([3.2, 4.8, 7.1, 9.1, 10.8])
slope, intercept = fit_line(xs, ys)
print("slope", round(float(slope), 3))
print("intercept", round(float(intercept), 3))
