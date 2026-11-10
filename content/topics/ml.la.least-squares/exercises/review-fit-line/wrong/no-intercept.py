import numpy as np

xs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
ys = np.array([3.2, 4.8, 7.1, 9.1, 10.8])


def fit_line(xs, ys):
    return np.linalg.lstsq(xs.reshape(-1, 1), ys)[0]


print(np.round(fit_line(xs, ys), 3))
