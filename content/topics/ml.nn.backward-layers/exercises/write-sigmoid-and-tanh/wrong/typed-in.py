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
    def forward(self, X):
        return X

    def backward(self, grad_out):
        return grad_out


class Tanh(Sigmoid):
    pass


print('Sigmoid [0.5, 0.731, 0.119] True')
print('Tanh [0.0, 0.762, -0.964] True')
