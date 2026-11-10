def parameter_count(layers):
    """Every dense layer has in * out weights and out biases."""
    return sum(i * o + o for i, o in zip(layers, layers[1:]))


def training_seconds(flops, flop_rate, utilization):
    """The machine sustains only a fraction of its peak rate, so the time is the FLOPs over peak times that fraction."""
    return flops / (flop_rate * utilization)


LAYERS = [784, 256, 128, 10]
params = parameter_count(LAYERS)
print(f"parameters: {params:,}")
epoch_flops = 6 * params * 60_000
print(f"one epoch at 30 percent of 10 TFLOP/s: {training_seconds(epoch_flops, 10e12, 0.3) * 1000:.1f} ms")
