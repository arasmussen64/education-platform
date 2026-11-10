def parameter_count(layers):
    """Weights and biases of every dense layer: in * out + out."""
    return sum(i * o + o for i, o in zip(layers, layers[1:]))


def training_flops(layers, examples):
    """Forward (2 per weight) plus backward (4 per weight), for every example: three times the forward pass."""
    forward = sum(2 * i * o for i, o in zip(layers, layers[1:]))
    return 3 * forward * examples


LAYERS = [784, 256, 128, 10]
print(parameter_count(LAYERS), training_flops(LAYERS, 60_000))
print(parameter_count([4, 3, 2]), training_flops([4, 3, 2], 10))
