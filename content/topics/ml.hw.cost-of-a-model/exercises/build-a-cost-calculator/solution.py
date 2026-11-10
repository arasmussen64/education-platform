def parameter_count(layers):
    """Weights and biases of every dense layer."""
    return sum(i * o + o for i, o in zip(layers, layers[1:]))


def forward_flops(layers):
    """A multiply and an add per weight, per example."""
    return sum(2 * i * o for i, o in zip(layers, layers[1:]))


def training_flops(layers, examples):
    """Forward plus a backward pass of twice the forward, for every example."""
    return 3 * forward_flops(layers) * examples


def training_bytes(params, batch, activations_per_example, itemsize):
    """Four copies of the parameters (weights, gradients, two Adam moments) plus one batch of activations."""
    return params * 4 * itemsize + batch * activations_per_example * itemsize


def training_seconds(flops, flop_rate, utilization):
    """FLOPs over the rate the machine really sustains: its peak times the fraction of it that is used."""
    return flops / (flop_rate * utilization)


LAYERS = [784, 256, 128, 10]
print(parameter_count(LAYERS), forward_flops(LAYERS), training_flops(LAYERS, 60_000))
print(training_bytes(parameter_count(LAYERS), 64, sum(LAYERS), 4), training_bytes(10**9, 8, 2 * 10**6, 2))
print(round(training_seconds(training_flops(LAYERS, 60_000), 10e12, 1.0), 4), round(training_seconds(training_flops(LAYERS, 60_000), 10e12, 0.3), 4))
print(round(training_seconds(6 * 7e9 * 1e12, 1000 * 10e12, 0.4) / 86400, 1))
