import numpy as np


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


pred = np.array([2.5, 0.0, 2.1, 7.8])
target = np.array([3.0, -0.5, 2.0, 8.0])
miss = pred - target
print(miss, round(float(np.mean(miss**2)), 4))
print(np.round(2 * miss / len(miss), 3))

p = np.array([0.9, 0.6, 0.3, 0.05])
y = np.array([1.0, 1.0, 0.0, 1.0])
each = -(y * np.log(p) + (1 - y) * np.log(1 - p))
print(np.round(each, 3), round(float(each.mean()), 3))
print(round(float(-np.log(0.01)), 3), round(float((1 - 0.01) ** 2), 3))

z = np.array([2.0, 0.0, -1.0])
y = np.array([1.0, 0.0, 1.0])
p = sigmoid(z)
print(np.round(p, 3))
print(np.round(p - y, 3))

scores = np.array([2.0, 1.0, 0.1])
e = np.exp(scores - scores.max())
probs = e / e.sum()
print(np.round(probs, 3), round(float(probs.sum()), 6))
print(round(float(-np.log(probs[0])), 3))
