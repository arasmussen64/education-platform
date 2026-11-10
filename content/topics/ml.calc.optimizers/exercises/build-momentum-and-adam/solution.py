import numpy as np


def loss(p):
    return p[0] ** 2 + 100 * p[1] ** 2


def grad(p):
    return np.array([2 * p[0], 200 * p[1]])


def momentum(grad, p, rate, beta, steps):
    v = np.zeros(len(p))
    path = []
    for step in range(steps):
        v = beta * v + grad(p)
        p = p - rate * v
        path.append(p)
    return path


def adam(grad, p, rate, steps, beta1=0.9, beta2=0.999, eps=1e-8):
    m = np.zeros(len(p))
    s = np.zeros(len(p))
    path = []
    for t in range(1, steps + 1):
        g = grad(p)
        m = beta1 * m + (1 - beta1) * g
        s = beta2 * s + (1 - beta2) * g**2
        m_hat = m / (1 - beta1**t)
        s_hat = s / (1 - beta2**t)
        p = p - rate * m_hat / (np.sqrt(s_hat) + eps)
        path.append(p)
    return path


start = np.array([10.0, 1.0])
print("plain", round(float(loss(momentum(grad, start, 0.005, 0.0, 100)[-1])), 4))
print("momentum", round(float(loss(momentum(grad, start, 0.005, 0.9, 100)[-1])), 4))
print("adam", round(float(loss(adam(grad, start, 0.3, 100)[-1])), 4))
print("adam's first step", np.round(adam(grad, start, 0.3, 1)[0], 3))
