import numpy as np


def grad(x):
    return 2 * x


def adam(x, rate, steps, beta1=0.9, beta2=0.999, eps=1e-8):
    m = 0.0
    s = 0.0
    for t in range(steps):
        g = grad(x)
        m = beta1 * m + (1 - beta1) * g
        s = beta2 * s + (1 - beta2) * g
        m_hat = m / (1 - beta1**t)
        s_hat = s / (1 - beta2**t)
        x = x - rate * m_hat / (np.sqrt(s_hat) + eps)
    return x


for steps in (1, 2, 50):
    print(steps, round(float(adam(2.0, 0.1, steps)), 4))
