import numpy as np

x = np.array([1.0, 2.0])
w = np.array([0.5, -0.25])
b = 0.1
z = x @ w + b
print("one neuron: z = 0.5 * 1 + -0.25 * 2 + 0.1 =", round(float(z), 2), "| relu(z) =", round(float(max(z, 0.0)), 2))

W = np.array([[0.5, -1.0, 0.2], [-0.25, 0.5, 0.4]])
b3 = np.array([0.1, -0.3, -0.5])
print("a layer of 3 neurons on one input: z =", np.round(x @ W + b3, 2).tolist(), "| relu:", np.maximum(x @ W + b3, 0.0).round(2).tolist())
X = np.array([[1.0, 2.0], [0.0, 0.0], [-1.0, 1.0], [2.0, -2.0]])
print("the same layer on a batch of 4 rows:", (X @ W + b3).shape, "| row 0 is the single input's answer:", np.round((X @ W + b3)[0], 2).tolist())


class Dense:
    """A layer of neurons: every output is a weighted sum of every input plus a bias. W is (inputs, outputs)."""

    def __init__(self, n_in, n_out, seed=0):
        rng = np.random.default_rng(seed)
        self.W = rng.standard_normal((n_in, n_out)) / np.sqrt(n_in)
        self.b = np.zeros(n_out)

    def forward(self, X):
        return X @ self.W + self.b

    def parameters(self):
        return [self.W, self.b]


class ReLU:
    """Keeps the positive part of every value and zeroes the rest; it has nothing to learn."""

    def forward(self, X):
        return np.maximum(X, 0.0)

    def parameters(self):
        return []


class Sequential:
    """Layers run one after another; the output of each is the input of the next."""

    def __init__(self, layers):
        self.layers = layers

    def forward(self, X):
        for layer in self.layers:
            X = layer.forward(X)
        return X

    def parameters(self):
        return [p for layer in self.layers for p in layer.parameters()]


net = Sequential([Dense(35, 16, seed=1), ReLU(), Dense(16, 10, seed=2)])
batch = np.random.default_rng(0).standard_normal((8, 35))
h = batch
trace = [f"input {h.shape}"]
for layer in net.layers:
    h = layer.forward(h)
    trace.append(f"{type(layer).__name__} -> {h.shape}")
print(" | ".join(trace))
print("parameters:", sum(p.size for p in net.parameters()), "= 35 * 16 + 16 + 16 * 10 + 10")

first, second = Dense(35, 16, seed=1), Dense(16, 10, seed=2)
merged = Dense(35, 10)
merged.W, merged.b = first.W @ second.W, first.b @ second.W + second.b
print("two Dense layers with nothing between equal one Dense:", np.allclose(second.forward(first.forward(batch)), merged.forward(batch)), "| with a ReLU between:", np.allclose(net.forward(batch), merged.forward(batch)))

points = np.array([[0.0, 0.0], [2.0, 0.0], [0.0, 2.0], [2.0, 2.0], [-1.0, -1.0]])
print("a neuron with w = [1, 1] and b = -1.5 fires where x + y > 1.5:", (points @ np.array([1.0, 1.0]) - 1.5 > 0).tolist())
