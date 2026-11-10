import numpy as np


def numeric_gradient(f, param, h=1e-6):
    grad = np.zeros_like(param)
    for index in np.ndindex(param.shape):
        old = param[index]
        param[index] = old + h
        up = f()
        param[index] = old - h
        down = f()
        param[index] = old
        grad[index] = (up - down) / (2 * h)
    return grad


class Sigmoid:
    """Squashes to (0, 1); the gradient is out * (1 - out), so the output is what backward needs."""

    def forward(self, X):
        self.out = 1 / (1 + np.exp(-X))
        return self.out

    def backward(self, grad_out):
        return grad_out * self.out


class Tanh:
    """Squashes to (-1, 1); the gradient is 1 - out squared."""

    def forward(self, X):
        self.out = np.tanh(X)
        return self.out

    def backward(self, grad_out):
        return grad_out * (1 - self.out ** 2)


X = np.array([[0.0, 1.0, -2.0], [0.5, -0.5, 3.0]])
for layer in (Sigmoid(), Tanh()):
    out = layer.forward(X)
    analytic = layer.backward(np.ones_like(X))
    numeric = numeric_gradient(lambda: float(layer.forward(X).sum()), X)
    print(type(layer).__name__, np.round(out[0], 3).tolist(), bool(np.abs(analytic - numeric).max() < 1e-6))
