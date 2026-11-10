def training_bytes(params, batch, activations_per_example, itemsize):
    """Weights, gradients and Adam's two moments, four copies of the parameters, plus the activations of one batch."""
    state = params * 4 * itemsize
    activations = batch * activations_per_example * itemsize
    return state + activations


print(training_bytes(235_146, 64, 1_178, 4))
print(training_bytes(1_000_000_000, 8, 2_000_000, 4) / 1e9)
