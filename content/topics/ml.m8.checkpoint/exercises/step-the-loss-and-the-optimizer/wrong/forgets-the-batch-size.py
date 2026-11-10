import numpy as np


class SoftmaxCrossEntropy:
    def forward(self, logits, labels):
        shifted = logits - logits.max(axis=1, keepdims=True)
        log_probs = shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))
        self.probs = np.exp(log_probs)
        self.labels = labels
        return float(-log_probs[np.arange(len(labels)), labels].mean())

    def backward(self):
        grad = self.probs.copy()
        grad[np.arange(len(self.labels)), self.labels] -= 1
        return grad


class Adam:
    """Adam, with weight decay added to every gradient first."""

    def __init__(self, rate, weight_decay=0.0, beta1=0.9, beta2=0.999, eps=1e-8):
        self.rate, self.weight_decay = rate, weight_decay
        self.beta1, self.beta2, self.eps = beta1, beta2, eps
        self.m, self.v, self.t = None, None, 0

    def step(self, params, grads):
        if self.m is None:
            self.m = [np.zeros_like(p) for p in params]
            self.v = [np.zeros_like(p) for p in params]
        self.t += 1
        for i, (param, grad) in enumerate(zip(params, grads)):
            grad = grad + self.weight_decay * param
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * grad
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * grad ** 2
            m_hat = self.m[i] / (1 - self.beta1 ** self.t)
            v_hat = self.v[i] / (1 - self.beta2 ** self.t)
            param -= self.rate * m_hat / (np.sqrt(v_hat) + self.eps)


logits = np.array([[2.0, 0.0, -1.0], [0.0, 0.0, 0.0], [1000.0, 0.0, 0.0]])
labels = np.array([0, 1, 0])
loss = SoftmaxCrossEntropy()
print(round(loss.forward(logits, labels), 4), np.round(loss.backward()[1], 4).tolist())
W = np.array([2.0, -1.0, 0.5])
optimizer = Adam(0.1, weight_decay=0.5)
for step in range(3):
    optimizer.step([W], [np.zeros(3)])
print(np.round(W, 2).tolist())
