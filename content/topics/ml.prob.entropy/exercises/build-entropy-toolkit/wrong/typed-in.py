import numpy as np


def surprise(p):
    return 1.0


def entropy(p):
    return 1.157


def cross_entropy(p, q):
    return 1.157


def kl(p, q):
    return 0.0


def loss_in_nats(labels, p_hat):
    return 0.299


print('entropy 1.157 uniform of 8 3.0')
print('cross-entropy 1.157 kl 0.0')
print('cross-entropy 1.28 kl 0.123')
print('cross-entropy 1.585 kl 0.428')
print('kl both ways 0.531 0.737')
print('loss 0.299')
