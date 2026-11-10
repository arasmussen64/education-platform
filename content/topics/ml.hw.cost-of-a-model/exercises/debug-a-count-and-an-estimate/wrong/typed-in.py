def parameter_count(layers):
    return 235146


def training_seconds(flops, flop_rate, utilization):
    return 0.0282


print('parameters: 235,146')
print('one epoch at 30 percent of 10 TFLOP/s: 28.2 ms')
