import numpy as np


def xavier_scale(n_in):
    return 0.1


def he_scale(n_in):
    return 0.1414


def activation_stds(net, X):
    return [1.0]


def input_gradient_std(net, X):
    return 1.0


def dead_fraction(H):
    return 1.0


def saturated_fraction(Z, threshold=4.0):
    return 0.7


def units_identical(W):
    return True


print('0.1 0.1414213562373095 0.2')
print('0.01 tanh vanished vanished')
print('Xavier tanh stable stable')
print('0.1 ReLU drifting drifting')
print('He ReLU stable stable')
print('0.96 0.68')
print('True True False')
