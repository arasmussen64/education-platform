import numpy as np


class Dropout:
    """Inverted dropout: in training, zero each value with probability p and scale the survivors by 1 / (1 - p), so the expected sum is unchanged and eval needs no correction."""

    def __init__(self, p, seed=0):
        self.p = p
        self.rng = np.random.default_rng(seed)
        self.training = True

    def forward(self, X):
        if not self.training or self.p == 0:
            self.mask = None
            return X
        self.mask = (self.rng.random(X.shape) >= ...) / (1 - ...)
        return X * self.mask

    def backward(self, grad_out):
        return grad_out if self.mask is None else grad_out * self.mask


layer = Dropout(0.5, seed=0)
X = np.ones((1000, 20))
dropped = layer.forward(X)
print(round(float((dropped == 0).mean()), 1), round(float(dropped.mean()), 1), np.unique(dropped).tolist())
layer.training = False
print(bool((layer.forward(X) == X).all()))
