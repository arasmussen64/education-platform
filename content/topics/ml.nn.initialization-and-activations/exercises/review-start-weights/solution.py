import numpy as np


def xavier_scale(n_in):
    return float(np.sqrt(1 / n_in))


def he_scale(n_in):
    return float(np.sqrt(2 / n_in))


def start_weights(n_in, n_out, activation, seed=0):
    """Standard normals times He's scale for ReLU and Xavier's for anything else, with zero biases."""
    scale = he_scale(n_in) if activation == "relu" else xavier_scale(n_in)
    W = np.random.default_rng(seed).standard_normal((n_in, n_out)) * scale
    return W, np.zeros(n_out)


W, b = start_weights(100, 50, "relu", seed=1)
print(W.shape, b.tolist() == [0.0] * 50, round(float(W.std()), 2))
W, b = start_weights(100, 50, "tanh", seed=1)
print(round(float(W.std()), 2))
