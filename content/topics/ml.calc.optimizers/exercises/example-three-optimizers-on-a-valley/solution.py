import numpy as np


def loss(p):
    return p[0] ** 2 + 100 * p[1] ** 2


def grad(p):
    return np.array([2 * p[0], 200 * p[1]])


def plain(p, rate, steps):
    for step in range(steps):
        p = p - rate * grad(p)
    return p


def momentum(p, rate, beta, steps):
    v = np.zeros(len(p))
    for step in range(steps):
        v = beta * v + grad(p)
        p = p - rate * v
    return p


def plain_decayed(p, rate, steps):
    for step in range(steps):
        p = p - rate * 0.5 ** (step // 100) * grad(p)
    return p


def adam(p, rate, steps, beta1=0.9, beta2=0.999, eps=1e-8):
    m = np.zeros(len(p))
    s = np.zeros(len(p))
    for t in range(1, steps + 1):
        g = grad(p)
        m = beta1 * m + (1 - beta1) * g
        s = beta2 * s + (1 - beta2) * g**2
        m_hat = m / (1 - beta1**t)
        s_hat = s / (1 - beta2**t)
        p = p - rate * m_hat / (np.sqrt(s_hat) + eps)
    return p


start = np.array([10.0, 1.0])
checkpoints = (10, 50, 100, 200)
print("plain", [round(float(loss(plain(start, 0.005, n))), 4) for n in checkpoints])
print("momentum", [round(float(loss(momentum(start, 0.005, 0.9, n))), 4) for n in checkpoints])
print(np.round([plain(start, 0.009, n) for n in (1, 2, 3)], 3))
print("rate 0.015", round(float(loss(plain(start, 0.015, 10))), 1))
print("fixed 0.01", [round(float(loss(plain(start, 0.01, n))), 4) for n in checkpoints])
print("decayed 0.01", [round(float(loss(plain_decayed(start, 0.01, n))), 4) for n in checkpoints])
print("adam", [round(float(loss(adam(start, 0.3, n))), 4) for n in checkpoints])
print("adam's first step", np.round(adam(start, 0.3, 1), 3))
