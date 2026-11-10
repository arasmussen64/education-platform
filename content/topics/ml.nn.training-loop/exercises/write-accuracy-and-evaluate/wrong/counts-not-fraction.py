import numpy as np


def accuracy(logits, labels):
    """The share of rows whose largest logit is the true class."""
    return float((logits.argmax(axis=1) == labels).sum())


def evaluate(net, loss, X, y):
    """Loss and accuracy on a whole set, with no training step."""
    logits = net.forward(X)
    return loss.forward(logits, y), accuracy(logits, y)


class Constant:
    """A stand-in network that always returns the same logits."""

    def __init__(self, logits):
        self.logits = logits

    def forward(self, X):
        return self.logits


class ZeroOneLoss:
    """A stand-in loss: the share of rows whose largest logit is not the true class."""

    def forward(self, logits, labels):
        return float((logits.argmax(axis=1) != labels).mean())


logits = np.array([[2.0, 1.0, 0.0], [0.1, 0.2, 0.7], [1.0, 3.0, 2.0], [0.5, 0.4, 0.3]])
labels = np.array([0, 2, 2, 1])
print(accuracy(logits, labels))
print(evaluate(Constant(logits), ZeroOneLoss(), np.zeros((4, 2)), labels))
