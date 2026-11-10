import numpy as np


def bowl(p):
    x, y = p
    return x**2 + 3 * y**2


def grad_bowl(p):
    x, y = p
    return np.array([2 * x, 6 * y])


p = np.array([4.0, 2.0])
for step in range(11):
    if step in (0, 1, 2, 5, 10):
        print(step, np.round(p, 3), round(float(bowl(p)), 4))
    p = p - 0.1 * grad_bowl(p)

for rate in [0.05, 0.1, 0.3, 0.4]:
    p = np.array([4.0, 2.0])
    for step in range(10):
        p = p - rate * grad_bowl(p)
    print(rate, round(float(bowl(p)), 3))

points = np.array([
    [0.0, 0.0, 3.1],
    [1.0, 0.0, 4.9],
    [0.0, 1.0, 2.05],
    [2.0, 3.0, 3.95],
    [3.0, 1.0, 8.1],
    [1.0, 2.0, 2.9],
])
A = np.column_stack([points[:, 0], points[:, 1], np.ones(6)])
z = points[:, 2]
w = np.zeros(3)
losses = []
for step in range(2000):
    miss = A @ w - z
    losses.append(float(np.mean(miss**2)))
    w = w - 0.1 * (2 / 6) * (A.T @ miss)
print(round(losses[0], 4), round(losses[10], 4), round(losses[100], 4), round(losses[-1], 4))
print(np.round(w, 3))
print(np.allclose(w, np.linalg.lstsq(A, z)[0], atol=1e-6))
