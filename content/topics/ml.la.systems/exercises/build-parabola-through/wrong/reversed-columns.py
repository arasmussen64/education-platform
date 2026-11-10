import numpy as np


def parabola_through(points):
    pts = np.array(points, dtype=float)
    xs = pts[:, 0]
    ys = pts[:, 1]
    A = np.column_stack([np.ones(3), xs, xs**2])
    if np.linalg.matrix_rank(A) < 3:
        return None
    return np.linalg.solve(A, ys)


print(parabola_through([(0, 1), (1, 3), (2, 9)]))
