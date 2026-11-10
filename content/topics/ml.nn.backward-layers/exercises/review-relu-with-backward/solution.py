import numpy as np


class ReLU:
    """Remembers where the input was positive; the gradient passes through there and is zero elsewhere."""

    def forward(self, X):
        self.mask = X > 0
        return np.maximum(X, 0.0)

    def backward(self, grad_out):
        return grad_out * self.mask


layer = ReLU()
print(layer.forward(np.array([[2.0, -1.0, 0.0], [-0.5, 3.0, 1.0]])).tolist())
print(layer.backward(np.array([[1.0, 1.0, 1.0], [0.5, -2.0, 4.0]])).tolist())
