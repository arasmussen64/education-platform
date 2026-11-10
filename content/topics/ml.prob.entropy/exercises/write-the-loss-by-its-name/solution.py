import numpy as np

labels = np.array([1.0, 0.0, 1.0, 1.0])
p_hat = np.array([0.9, 0.2, 0.7, 0.6])


def cross_entropy_loss(labels, p_hat):
    picked = np.where(labels == 1, p_hat, 1 - p_hat)
    return float(np.mean(-np.log(picked)))


print(round(cross_entropy_loss(labels, p_hat), 4))
print(round(float(-np.mean(labels * np.log(p_hat) + (1 - labels) * np.log(1 - p_hat))), 4))
print(round(cross_entropy_loss(labels, labels * 0.999 + 0.0005), 4), round(cross_entropy_loss(labels, np.full(4, 0.5)), 4))
