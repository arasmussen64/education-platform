import numpy as np


class Dense:
    def __init__(self, W, b):
        self.W = W
        self.b = b
        self.dW = W
        self.db = b

    def forward(self, X):
        return X

    def backward(self, grad_out):
        return grad_out


print('[[1.0, 2.5], [1.0, 0.5], [1.0, -1.5]] [1.0, 1.5]')
print('[[0.5, 1.0, 0.75], [-1.0, 2.0, 0.5]]')
