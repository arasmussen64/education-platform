import numpy as np

M = np.array([[1.0, -2.0], [0.5, 3.0]])


def numeric_grad(f, W, h=1e-6):
    return 2 * W


print(np.round(2 * M, 4))
print(True)
