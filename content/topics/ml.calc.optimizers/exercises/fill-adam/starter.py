import numpy as np


def grad(x):
    return 2 * x


def adam_steps(x, rate, steps, beta1=0.9, beta2=0.999, eps=1e-8):
    m = 0.0
    s = 0.0
    path = []
    for t in range(1, steps + 1):
        g = grad(x)
        m = beta1 * m + (1 - beta1) * g
        s = beta2 * s + (1 - beta2) * g**2
        m_hat = m / (1 - beta1**...)
        s_hat = s / (1 - beta2**t)
        x = x - rate * m_hat / (np.sqrt(...) + eps)
        path.append(round(float(x), 4))
    return path


print(adam_steps(2.0, 0.1, 3))
print(adam_steps(-50.0, 0.1, 3))
