import numpy as np


def solve_2x2(rows):
    rows = rows.astype(float).copy()
    factor = rows[1, 0] / ...
    rows[1] = rows[1] - ... * rows[0]
    y = rows[1, 2] / ...
    x = (rows[0, 2] - rows[0, 1] * y) / rows[0, 0]
    return x, y


x, y = solve_2x2(np.array([[2.0, 1.0, 5.0], [1.0, -1.0, 1.0]]))
print(x, y)
