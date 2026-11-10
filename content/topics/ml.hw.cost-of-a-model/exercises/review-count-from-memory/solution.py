def parameter_count(layers):
    """Weights and biases of every dense layer: in * out + out."""
    return sum(i * o + o for i, o in zip(layers, layers[1:]))


print(parameter_count([784, 256, 128, 10]), parameter_count([4, 3, 2]))
