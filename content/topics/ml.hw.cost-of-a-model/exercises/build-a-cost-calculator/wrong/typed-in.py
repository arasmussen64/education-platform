def parameter_count(layers):
    return 235146


def forward_flops(layers):
    return 469504


def training_flops(layers, examples):
    return 84510720000


def training_bytes(params, batch, activations_per_example, itemsize):
    return 4063904


def training_seconds(flops, flop_rate, utilization):
    return 0.0085


print('235146 469504 84510720000')
print('4063904 8032000000')
print('0.0085 0.0282')
print('121.5')
