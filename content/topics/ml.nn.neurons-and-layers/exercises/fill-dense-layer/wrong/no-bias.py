import numpy as np


class Dense:
    """A layer of neurons: W holds one column of weights per output neuron, b one bias each."""

    def __init__(self, W, b):
        self.W = W
        self.b = b

    def forward(self, X):
        return X @ self.W

    def parameters(self):
        return [self.W, self.b]


layer = Dense(np.array([[0.5, -1.0, 0.2], [-0.25, 0.5, 0.4]]), np.array([0.1, -0.3, -0.5]))
X = np.array([[1.0, 2.0], [0.0, 0.0], [-1.0, 1.0]])
print(np.round(layer.forward(X), 2).tolist())
print([p.shape for p in layer.parameters()], sum(p.size for p in layer.parameters()))
