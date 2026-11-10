def model_cost(layers, examples, batch, itemsize):
    """(parameters, training FLOPs, bytes): in * out + out per dense layer; 6 FLOPs per parameter per example; four copies of the parameters plus one batch of activations."""
    params = sum(i * o + o for i, o in zip(layers, layers[1:]))
    flops = 6 * params * examples
    bytes_needed = params * 4 * itemsize + batch * sum(layers) * itemsize
    return params, flops, bytes_needed


print(model_cost([4, 64, 32, 5], 400, 32, 4))
print(model_cost([4, 3, 2], 10, 2, 2))
