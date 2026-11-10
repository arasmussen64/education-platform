import numpy as np

X = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [2.0, 3.0]])
A = np.column_stack([X, np.ones(4)])
z = np.array([3.0, 5.0, 2.0, 4.0])


def numeric_gradient(f, p, h=1e-6):
    grad = np.zeros(len(p))
    for i in range(len(p)):
        step = np.zeros(len(p))
        step[i] = h
        grad[i] = (f(p + step) - f(p - step)) / (2 * h)
    return grad


def mse(w):
    return np.mean((A @ w - z) ** 2)


def mse_gradient(w):
    return 2 / len(z) * (A.T @ (A @ w - z))


print(mse_gradient(np.zeros(3)))
for w in [np.zeros(3), np.array([1.0, 1.0, 1.0])]:
    print(np.allclose(mse_gradient(w), numeric_gradient(mse, w)))
