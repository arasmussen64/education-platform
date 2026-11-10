import numpy as np


class Dense:
    """A dense layer that remembers its input, so backward can compute the gradient for W."""

    def __init__(self, W, b):
        self.W = W
        self.b = b

    def forward(self, X):
        self.X = X
        return X @ self.W + self.b

    def backward(self, grad_out):
        self.dW = ... @ grad_out
        self.db = grad_out.sum(axis=...)
        return grad_out @ ...


layer = Dense(np.array([[1.0, -1.0], [0.0, 2.0], [0.5, 0.5]]), np.array([-0.5, 0.0]))
X = np.array([[1.0, 1.0, 1.0], [2.0, 0.0, -2.0]])
layer.forward(X)
grad_in = layer.backward(np.array([[1.0, 0.5], [0.0, 1.0]]))
print(layer.dW.tolist(), layer.db.tolist())
print(grad_in.tolist())
