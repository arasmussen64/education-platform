LAYERS = [784, 256, 128, 10]


def parameter_count(layers):
    """Every dense layer has in * out weights and out biases."""
    return sum(i * o + o for i, o in zip(layers, layers[1:]))


def forward_flops(layers):
    """A multiply and an add per weight for each example; the biases and activations are a rounding error beside them."""
    return sum(2 * i * o for i, o in zip(layers, layers[1:]))


params = parameter_count(LAYERS)
forward = forward_flops(LAYERS)
print(f"layers {LAYERS}: {params:,} parameters; a forward pass is {forward:,} FLOPs per example, {forward / params:.2f} per parameter")
backward = 2 * forward
print(f"the backward pass is about twice that, {backward:,} (a gradient for the inputs and one for the weights), so a training step is {forward + backward:,} per example, about 6 per parameter")
batch = 64
print(f"a batch of {batch}: {(forward + backward) * batch:,} FLOPs")

print(f"weights in float32: {params * 4:,} bytes | in float16: {params * 2:,}")
activations = sum(LAYERS)
print(f"activations kept for the backward pass: {activations:,} values per example; a batch of {batch} is {activations * batch * 4:,} bytes in float32, {activations * batch * 2:,} in float16")
print(f"training state with Adam in float32 (weights, gradients, two moments): {4 * 4} bytes per parameter, {params * 16:,} bytes | mixed precision (float16 weights and gradients, float32 master weights and moments): {2 + 2 + 4 + 4 + 4} bytes per parameter")

GPU = 10e12
examples = 60_000
epoch = 6 * params * examples
print(f"one epoch of {examples:,} examples: {epoch:.3g} FLOPs, {epoch / GPU * 1000:.1f} ms on a 10 TFLOP/s GPU at full speed, {epoch / (GPU * 0.3) * 1000:.0f} ms at a realistic 30 percent")
big_flops = 6 * 7e9 * 1e12
print(f"a 7 billion parameter model on a trillion tokens: {big_flops:.3g} FLOPs, {big_flops / GPU / 86400 / 365:.0f} years on that GPU, {big_flops / (1000 * GPU * 0.4) / 86400:.0f} days on 1,000 of them at 40 percent")
