import numpy as np

M = np.array([[1.0, -2.0], [0.5, 3.0]])


def numeric_grad(f, W, h=1e-6):
    grad = np.zeros_like(W)
    for index in np.ndindex(W.shape):
        grad[index] = (f(W + h) - f(W - h)) / (2 * h)
    return grad


print(np.round(numeric_grad(lambda W: np.sum(W**2), M), 4))
print(np.allclose(numeric_grad(lambda W: np.sum(W**2), M), 2 * M, atol=1e-6))
