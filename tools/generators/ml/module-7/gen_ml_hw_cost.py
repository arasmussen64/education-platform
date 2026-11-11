"""Writes the topic ml.hw.cost-of-a-model (Module 7's sixth topic). Run from
the repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Everything is arithmetic on layer sizes: parameters, FLOPs, bytes and an
estimate of time; no package is needed. Files are written as bytes with LF
endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.hw.cost-of-a-model")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str) -> str:
    result = subprocess.run([sys.executable, "-W", "error", "-c", program], capture_output=True, text=True, check=True)
    return result.stdout.replace("\r\n", "\n")


def block(text: str, indent: str = "  ") -> str:
    return "".join(indent + line + "\n" for line in text.rstrip("\n").splitlines())


def quoted(text: str) -> str:
    """A single-quoted YAML scalar: the one place where '' is an apostrophe."""
    return "'" + text.replace("'", "''") + "'"


def mcq(item_id: str, prompt: str, choices: list[str], answer: int, explanation: str, skills: list[str]) -> None:
    """An MCQ whose right answer is never the longest choice, with plain apostrophes in the block scalars."""
    lengths = [len(c) for c in choices]
    assert lengths[answer] < max(length for i, length in enumerate(lengths) if i != answer), (item_id, lengths)
    assert "''" not in prompt and "''" not in explanation, item_id
    write(
        f"recall/{item_id}.yaml",
        f"id: {item_id}\ntype: mcq\nrev: 1\nprompt: |\n{block(prompt)}choices:\n"
        + "".join(f"  - {quoted(c)}\n" for c in choices)
        + f"answer: {answer}\nexplanation: |\n{block(explanation)}skills: [{', '.join(skills)}]\n",
    )


# --- the worked example ----------------------------------------------------------------------

EXAMPLE = '''LAYERS = [784, 256, 128, 10]


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
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert len(EX) == 8, EX
assert EX[0] == "layers [784, 256, 128, 10]: 235,146 parameters; a forward pass is 469,504 FLOPs per example, 2.00 per parameter", EX[0]
assert EX[1] == "the backward pass is about twice that, 939,008 (a gradient for the inputs and one for the weights), so a training step is 1,408,512 per example, about 6 per parameter", EX[1]
assert EX[2] == "a batch of 64: 90,144,768 FLOPs", EX[2]
assert EX[3] == "weights in float32: 940,584 bytes | in float16: 470,292", EX[3]
assert EX[4] == "activations kept for the backward pass: 1,178 values per example; a batch of 64 is 301,568 bytes in float32, 150,784 in float16", EX[4]
assert EX[5] == "training state with Adam in float32 (weights, gradients, two moments): 16 bytes per parameter, 3,762,336 bytes | mixed precision (float16 weights and gradients, float32 master weights and moments): 16 bytes per parameter", EX[5]
assert EX[6] == "one epoch of 60,000 examples: 8.47e+10 FLOPs, 8.5 ms on a 10 TFLOP/s GPU at full speed, 28 ms at a realistic 30 percent", EX[6]
assert EX[7] == "a 7 billion parameter model on a trillion tokens: 4.2e+22 FLOPs, 133 years on that GPU, 122 days on 1,000 of them at 40 percent", EX[7]
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_PARAMS = '''def parameter_count(layers):
    return sum(i * o + o for i, o in zip(layers, layers[1:]))


def forward_flops(layers):
    return sum(2 * i * o for i, o in zip(layers, layers[1:]))


print(parameter_count([4, 3, 2]), forward_flops([4, 3, 2]))
print(parameter_count([100, 100]), forward_flops([100, 100]), 6 * parameter_count([100, 100]))
'''
PREDICT_PARAMS_OUT = out(PREDICT_PARAMS)
assert PREDICT_PARAMS_OUT == "23 36\n10100 20000 60600\n", PREDICT_PARAMS_OUT

PREDICT_BYTES = '''params = 1_000_000
print(params * 4, params * 2)
print(params * (4 + 4 + 4 + 4), params * (2 + 2 + 4 + 4 + 4))
batch, activations_per_example = 32, 5_000
print(batch * activations_per_example * 4, batch * activations_per_example * 2)
'''
PREDICT_BYTES_OUT = out(PREDICT_BYTES)
assert PREDICT_BYTES_OUT == "4000000 2000000\n16000000 16000000\n640000 320000\n", PREDICT_BYTES_OUT

REVIEW_WIDER = '''def parameter_count(layers):
    return sum(i * o + o for i, o in zip(layers, layers[1:]))


narrow, wide, deep = [100, 100, 10], [100, 200, 10], [100, 100, 100, 10]
print(parameter_count(narrow), parameter_count(wide), parameter_count(deep))
'''
REVIEW_WIDER_OUT = out(REVIEW_WIDER)
assert REVIEW_WIDER_OUT == "11110 22210 21210\n", REVIEW_WIDER_OUT

PARSONS_LINES = [
    "params, examples, epochs = 235_146, 60_000, 10",
    "flops = 6 * params * examples * epochs",
    "seconds = flops / (10e12 * 0.3)",
    "print(round(seconds, 2))",
]
assert out("\n".join(PARSONS_LINES) + "\n") == "0.28\n"
assert out("\n".join(PARSONS_LINES).replace("flops = 6 *", "flops = 2 *") + "\n") != "0.28\n"

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''def training_bytes(params, batch, activations_per_example, itemsize):
    """Weights, gradients and Adam's two moments, four copies of the parameters, plus the activations of one batch."""
    state = params * 4 * itemsize
    activations = batch * activations_per_example * itemsize
    return state + activations


print(training_bytes(235_146, 64, 1_178, 4))
print(training_bytes(1_000_000_000, 8, 2_000_000, 4) / 1e9)
'''
FILL_STARTER = FILL_SOLUTION.replace("    state = params * 4 * itemsize\n", "    state = params * ... * itemsize\n").replace("    activations = batch * activations_per_example * itemsize\n", "    activations = ... * activations_per_example * itemsize\n")
FILL_WRONG = FILL_SOLUTION.replace("    state = params * 4 * itemsize\n", "    state = params * itemsize\n")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "4063904\n16.064\n", FILL_OUT
assert out(FILL_WRONG) != FILL_OUT

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''def parameter_count(layers):
    """Weights and biases of every dense layer: in * out + out."""
    return sum(i * o + o for i, o in zip(layers, layers[1:]))


def training_flops(layers, examples):
    """Forward (2 per weight) plus backward (4 per weight), for every example: three times the forward pass."""
    forward = sum(2 * i * o for i, o in zip(layers, layers[1:]))
    return 3 * forward * examples


LAYERS = [784, 256, 128, 10]
print(parameter_count(LAYERS), training_flops(LAYERS, 60_000))
print(parameter_count([4, 3, 2]), training_flops([4, 3, 2], 10))
'''
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "235146 84510720000\n23 1080\n", WRITE_OUT
WRITE_NO_BIAS = WRITE_SOLUTION.replace("    return sum(i * o + o for i, o in zip(layers, layers[1:]))", "    return sum(i * o for i, o in zip(layers, layers[1:]))")
WRITE_FORWARD_ONLY = WRITE_SOLUTION.replace("    return 3 * forward * examples", "    return forward * examples")
assert out(WRITE_NO_BIAS) != WRITE_OUT and out(WRITE_FORWARD_ONLY) != WRITE_OUT

# --- the build ----------------------------------------------------------------------------------

BUILD_SOLUTION = '''def parameter_count(layers):
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
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == "235146 469504 84510720000\n4063904 8032000000\n0.0085 0.0282\n121.5\n", BUILD_OUT
BUILD_NO_BIAS = BUILD_SOLUTION.replace("    return sum(i * o + o for i, o in zip(layers, layers[1:]))", "    return sum(i * o for i, o in zip(layers, layers[1:]))")
BUILD_FORWARD_TWICE = BUILD_SOLUTION.replace("    return 3 * forward_flops(layers) * examples", "    return 2 * forward_flops(layers) * examples")
BUILD_ONE_COPY = BUILD_SOLUTION.replace("    return params * 4 * itemsize + batch * activations_per_example * itemsize", "    return params * itemsize + batch * activations_per_example * itemsize")
BUILD_TIMES_UTILIZATION = BUILD_SOLUTION.replace("    return flops / (flop_rate * utilization)", "    return flops / flop_rate * utilization")
for wrong in (BUILD_NO_BIAS, BUILD_FORWARD_TWICE, BUILD_ONE_COPY, BUILD_TIMES_UTILIZATION):
    assert wrong != BUILD_SOLUTION and out(wrong) != BUILD_OUT

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''def parameter_count(layers):
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
'''
BUG_BIAS = ("    return sum(i * o + o for i, o in zip(layers, layers[1:]))", "    return sum(i * o for i, o in zip(layers, layers[1:]))")
BUG_UTILIZATION = ("    return flops / (flop_rate * utilization)", "    return flops / flop_rate * utilization")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_BIAS).replace(*BUG_UTILIZATION)
DEBUG_STILL_BIAS = DEBUG_SOLUTION.replace(*BUG_BIAS)
DEBUG_STILL_UTILIZATION = DEBUG_SOLUTION.replace(*BUG_UTILIZATION)
DEBUG_OUT = out(DEBUG_SOLUTION)
STARTER_OUT = out(DEBUG_STARTER)
print("debug:\n" + DEBUG_OUT + "starter:\n" + STARTER_OUT)
assert DEBUG_OUT == "parameters: 235,146\none epoch at 30 percent of 10 TFLOP/s: 28.2 ms\n", DEBUG_OUT
assert STARTER_OUT == "parameters: 234,752\none epoch at 30 percent of 10 TFLOP/s: 2.5 ms\n", STARTER_OUT
assert out(DEBUG_STILL_BIAS) != DEBUG_OUT and out(DEBUG_STILL_UTILIZATION) != DEBUG_OUT

REVIEW_CODE_SOLUTION = '''def parameter_count(layers):
    """Weights and biases of every dense layer: in * out + out."""
    return sum(i * o + o for i, o in zip(layers, layers[1:]))


print(parameter_count([784, 256, 128, 10]), parameter_count([4, 3, 2]))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "235146 23\n", REVIEW_CODE_OUT
REVIEW_CODE_WRONG = REVIEW_CODE_SOLUTION.replace("    return sum(i * o + o for i, o in zip(layers, layers[1:]))", "    return sum(i * o for i, o in zip(layers, layers[1:]))")
assert out(REVIEW_CODE_WRONG) != REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.hw.cost-of-a-model
kind: topic
status: ready
title: "Counting a model's cost"
summary: "Parameters, FLOPs and bytes: counting a network's weights, the operations of a forward and backward pass, memory for weights and activations at float32 and float16, and an estimate of time from a GPU's throughput."
prerequisites: [ml.hw.parallelism-and-gpus, ml.hw.floating-point]
estimated_minutes: 50
rev: 1
objectives:
  - "Count the parameters of a network from its layer sizes."
  - "Count the FLOPs of a forward pass and estimate the backward pass, for one example and for a batch."
  - "Compute the memory for weights and activations at float32 and float16, and say what mixed precision trades."
  - "Estimate training time from FLOPs and a GPU's throughput, and say why the estimate is optimistic."
# Linked, never copied or embedded: Wikipedia is CC BY-SA 4.0; the paper is
# on arXiv under its non-exclusive distribution licence.
resources:
  - title: "Wikipedia: Neural scaling law (the Cost of training section and the Chinchilla scaling example, where training FLOPs are about 6 times parameters times tokens)"
    url: https://en.wikipedia.org/wiki/Neural_scaling_law
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
  - title: "Wikipedia: Mixed-precision arithmetic (what is kept in float32 and what is done in float16, and why)"
    url: https://en.wikipedia.org/wiki/Mixed-precision_arithmetic
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
  - title: "Hoffmann et al. 2022, Training Compute-Optimal Large Language Models, Appendix F (how the FLOPs of a transformer are counted, layer by layer)"
    url: https://arxiv.org/abs/2203.15556
    type: reading
    use: link
    license: "arXiv non-exclusive distribution licence (linked, not copied)"
practice:
  - example-the-cost-of-a-network
  - predict-parameters-and-flops
  - mcq-six-per-parameter
  - parsons-training-flops
  - predict-bytes
  - mcq-what-dominates-memory
  - mcq-what-mixed-precision-trades
  - mcq-why-the-estimate-is-optimistic
  - fill-training-bytes
  - write-count-a-network
prove:
  build: build-a-cost-calculator
  debug: debug-a-count-and-an-estimate
  explain:
    prompt: |
      A teammate estimated that a model would train in an hour on their laptop and it took a day; another asks whether a network of a billion parameters can be trained on a GPU with 24 gigabytes of memory, or at least run; a third asks what switching to mixed precision would give them. In your own words: how you count a network's parameters from its layer sizes and the FLOPs of its forward and backward passes, and the rule of thumb for a training step; how much memory the weights, the gradients, the optimizer state and the activations take at float32 and float16, and what mixed precision changes; and how to estimate training time from FLOPs and a GPU's throughput, and why the first teammate's estimate was a day out.
    rubric:
      - id: parameters
        required: true
        description: "A dense layer from i inputs to o outputs has i times o weights and o biases; the network's parameters are the sum over its layers. For [784, 256, 128, 10] that is 235,146."
      - id: flops
        required: true
        description: "A forward pass is a multiply and an add per weight per example, about 2 FLOPs per parameter; the backward pass is about twice the forward (a gradient for the inputs and one for the weights), so a training step is about 6 FLOPs per parameter per example, times the batch, times the examples seen."
      - id: memory
        required: true
        description: "Weights are parameters times bytes per value (4 in float32, 2 in float16); training with Adam keeps weights, gradients and two moments, 16 bytes per parameter in float32, and mixed precision keeps a float32 master copy so the state stays about 16; activations scale with the batch and are halved by float16. A billion parameters is 2 GB to run in float16 and 16 GB of state to train before any activations."
      - id: time
        required: true
        description: "Time is FLOPs over the rate the machine sustains, which is its peak times a utilization of perhaps 30 to 50 percent, because of memory-bound steps, small matrix multiplies, data loading, Python overhead and communication; a peak-rate estimate is optimistic by that factor and more, and a laptop CPU is far below a GPU's rate to begin with."
    model_answer: |
      A dense layer from i inputs to o outputs has i times o weights and o biases, so a network's parameter count is the sum of i times o plus o over its layers: the [784, 256, 128, 10] network is 200,960 plus 32,896 plus 1,290, which is 235,146. The forward pass does a multiply and an add for every weight for every example, so it is about 2 FLOPs per parameter; the biases and the activation functions are a rounding error beside the matrix multiplies. The backward pass computes a gradient with respect to the inputs of each layer and one with respect to its weights, each another matrix multiply of the same size, so it is about twice the forward. That gives the rule of thumb: a training step costs about 6 FLOPs per parameter per example, and a whole run costs 6 times the parameters times the number of examples, or tokens, seen. Memory is parameters times bytes per value, 4 in float32 and 2 in float16, for the weights alone. Training with Adam keeps four copies, the weights, the gradients and the two moment estimates, 16 bytes per parameter in float32, and on top of that the activations of every layer for the current batch, which scale with the batch size and are the part that halves when the batch is computed in float16. So the billion-parameter network is 2 gigabytes to run in float16, which fits, and 16 gigabytes of training state before a single activation, which with a useful batch does not fit in 24 gigabytes without tricks such as a smaller optimizer, sharding the state across GPUs or recomputing activations. Mixed precision runs the matrix multiplies and stores the activations in float16 or bfloat16 while keeping a float32 master copy of the weights and the optimizer moments, so the state stays about 16 bytes per parameter; what it buys is halved activation memory, halved memory traffic for the memory-bound steps, and a much higher matrix-multiply rate on the tensor cores, which the third teammate would feel as a step that is two to three times faster. The price is float16's narrow range, which needs loss scaling to keep small gradients from flushing to zero, or bfloat16, which keeps float32's range with fewer digits. Time is FLOPs divided by the rate the machine really sustains. The peak number on the spec sheet assumes every unit is busy every cycle; in practice a training loop reaches perhaps 30 to 50 percent of it, because the elementwise steps are memory-bound, the matrix multiplies are sometimes small, the data has to be loaded and moved, Python glue runs between the kernels and, on several GPUs, gradients have to be exchanged. The first teammate most likely divided by the peak rate of a GPU-class number on a laptop CPU that sustains far less, and ignored utilization on top; an hour at peak becoming a day is a factor of 24, which is a few times for utilization multiplied by a few times for the hardware.
review_pool:
  - review-mcq-fits-on-the-gpu
  - review-mcq-twice-the-tokens
  - review-predict-wider-and-deeper
  - review-count-from-memory
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: parameters
    description: "Count a network's parameters from its layer sizes"
  - id: flops
    description: "Count the FLOPs of a forward pass and estimate the backward, per example and per batch"
  - id: memory
    description: "Compute the memory for weights, state and activations at float32 and float16, and say what mixed precision trades"
  - id: time
    description: "Estimate training time from FLOPs and throughput, and say why the estimate is optimistic"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    '''<Intro>

Before a model is trained, three numbers say whether it can be: how many **parameters** it has, how many **FLOPs** (floating-point operations, one add or one multiply each) a training step costs, and how many **bytes** it needs. All three come from the layer sizes with arithmetic you can do on paper, and from them follows an estimate of time on a given machine, which is always optimistic in ways this topic names. The network here is a small one (784 inputs, two hidden layers, 10 outputs) so that every count can be checked by hand; the same counting, done on a transformer, is how the cost of a large language model is estimated.

The main resource is **Wikipedia's _Neural scaling law_ page**, in particular its Cost of training section and its Chinchilla scaling example, where the rule that training costs about 6 FLOPs per parameter per token comes from; about 15 minutes. The _Mixed-precision arithmetic_ page says what is kept in float32 and what runs in float16. The Chinchilla paper's Appendix F is the layer-by-layer count for a transformer, for when you want to see the rule derived. Watch for:

- **6 × N × D**: parameters times tokens, times six.
- **The master copy**: why mixed precision keeps float32 weights.
- **Utilization**: the fraction of a GPU's peak that a real training loop reaches.

</Intro>

<Resource index={0} />

<Recap>

- **Parameters.** A dense layer from `i` inputs to `o` outputs has `i * o` weights and `o` biases. Sum over the layers: `[784, 256, 128, 10]` is 200,960 + 32,896 + 1,290 = **235,146**. Width costs more than depth: doubling one hidden layer's width doubles both weight blocks that touch it, doubling every layer's width quadruples the whole network, while adding a layer adds one more block.
- **FLOPs of a forward pass.** A multiply and an add for each weight, for each example: `2 * i * o` per layer, about **2 FLOPs per parameter**. The biases and activation functions are a rounding error beside the matrix multiplies. For a batch, multiply by the batch size.
- **The backward pass** (the pass that works out how the loss changes with every weight, so the weights can be updated) computes, for each layer, a gradient with respect to its inputs (to pass further back) and one with respect to its weights (to update them): two matrix multiplies of the same size as the forward one, so about **twice the forward**. A training step is therefore about **6 FLOPs per parameter per example**, and a whole run is `6 * N * D`, parameters times examples (or tokens, the pieces a language model's text is cut into) seen: 7 billion parameters on a trillion tokens is 4.2 × 10²² FLOPs.
- **Bytes for weights.** Parameters times bytes per value: 4 in float32, 2 in float16 or bfloat16. The small network is 940,584 bytes in float32. A billion parameters is 4 GB, or 2 GB in float16, to run.
- **Bytes for training.** Adam, the usual optimizer (the rule that turns gradients into weight updates), keeps the weights, the gradients and two running averages of the gradients, its moments: four copies, **16 bytes per parameter** in float32. A billion parameters is 16 GB of state before any activations. Mixed precision keeps a float32 master copy of the weights and the moments and adds float16 copies of the weights and gradients: 2 + 2 + 4 + 4 + 4, still about 16. The state is not where mixed precision saves memory.
- **Activations** are every layer's output for the current batch, kept for the backward pass: `sum(layers)` values per example, times the batch, times the bytes. They scale with the batch (and, in a transformer, with the sequence length) while the state does not, so at large batches they dominate, and they are what float16 halves. The fixes when they don't fit: a smaller batch, recomputing activations in the backward pass, or sharding (splitting the state) across GPUs.
- **What mixed precision trades.** Matrix multiplies and activations in float16 or bfloat16, master weights and optimizer in float32. Gains: half the activation memory, half the memory traffic on memory-bound steps, and a much higher matrix-multiply rate on tensor cores (the matrix-multiply units of recent GPUs), often a step two to three times faster. Cost: float16's range is narrow (largest value 65,504, smallest normal about 6 × 10⁻⁵), so small gradients flush to zero unless the loss is scaled up before the backward pass and the gradients scaled back down; bfloat16 keeps float32's range with only 8 significant bits (7 stored), and that range is why it is the usual choice when the hardware has it.
- **Time** is FLOPs over the rate the machine sustains, which is its peak times a **utilization**: one **epoch** (one pass over the training set) of 60,000 examples through the small network is 8.5 × 10¹⁰ FLOPs, 8.5 ms at the full 10 TFLOP/s of the round-number GPU and 28 ms at 30 percent. The estimate at peak is optimistic because the memory-bound steps don't use the arithmetic units, small matrix multiplies don't fill the GPU, data must be loaded and moved across the bus, Python runs between the kernels (the GPU's individual programs), and on several GPUs the gradients must be exchanged; 30 to 50 percent is a good run. The 7-billion-parameter model is 133 years on one such GPU and about four months on a thousand at 40 percent, which is why those runs happen on clusters.
- **In machine learning** (names you'll meet later): **model FLOPs utilization** (MFU) is the fraction above, reported for large runs; **scaling laws** relate loss to parameters and tokens under a compute budget, and the Chinchilla result is that the two should grow together; **parameter-efficient fine-tuning** (LoRA and friends) trains a small fraction of the parameters so that the 16 bytes of state are paid only for those; and a model card's "7B" is this topic's N.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/predict-parameters-and-flops.yaml",
    f'''id: predict-parameters-and-flops
type: predict_output
rev: 1
prompt: |
  The parameters and forward FLOPs of a tiny network, then of a single 100-by-100 layer with its training FLOPs per example. What does the program print?
code: |
{block(PREDICT_PARAMS)}expected_output: |
{block(PREDICT_PARAMS_OUT)}explanation: |
  `[4, 3, 2]` is two layers: 4 times 3 plus 3, then 3 times 2 plus 2, 15 plus 8 parameters; the forward pass is 2 FLOPs per weight, 2 times (12 plus 6). The single layer has 10,000 weights and 100 biases, a forward pass of 20,000 FLOPs, and a training step of about 6 per parameter.
skills: [parameters, flops]
''',
)

mcq(
    "mcq-six-per-parameter",
    "Why is a training step about 6 FLOPs per parameter per example, when the forward pass is 2?",
    [
        "Because the optimizer does 4 FLOPs per parameter to update the weights",
        "Because the backward pass is two matrix multiplies per layer, for the input gradient and the weight gradient, each the size of the forward one",
        "Because the loss is computed three times per step: once to check the batch, once to average it over the examples, and once more to report it to the log",
        "Because the gradients are computed in float64, which costs twice as much per operation",
    ],
    1,
    "The forward pass is one matrix multiply per layer, a multiply and an add per weight. Going backward, each layer needs the gradient with respect to its inputs, to pass to the layer before, and with respect to its weights, to update them; each is a matrix multiply of the same size, so the backward pass is about 4 per parameter and the step about 6. The optimizer's update is one or two operations per parameter, nothing beside the batch's matrix multiplies, and the precision doesn't change the count.",
    ["flops"],
)

write(
    "recall/parsons-training-flops.yaml",
    "id: parsons-training-flops\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to estimate how long ten epochs of 60,000 examples through the 235,146-parameter network take on a 10 TFLOP/s GPU at 30 percent utilization, and print `0.28` seconds. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("flops = 2 * params * examples * epochs")
    + "\nexplanation: |\n"
    + block("A training step is about 6 FLOPs per parameter per example, forward and backward together; the decoy counts only the forward pass. The machine sustains its peak times the utilization, 3 TFLOP/s here, and the FLOPs over that is 0.28 seconds.")
    + "skills: [flops, time]\n",
)

write(
    "recall/predict-bytes.yaml",
    f'''id: predict-bytes
type: predict_output
rev: 1
prompt: |
  The bytes of a million parameters as weights in float32 and float16, as full training state in float32 and in mixed precision, and the activations of a batch. What does the program print?
code: |
{block(PREDICT_BYTES)}expected_output: |
{block(PREDICT_BYTES_OUT)}explanation: |
  Weights alone are 4 bytes per parameter in float32 and 2 in float16. Training with Adam keeps four float32 copies, 16 bytes per parameter; mixed precision keeps float16 weights and gradients beside float32 master weights and two moments, 2 plus 2 plus 4 plus 4 plus 4, also 16. The activations of a batch are batch times values per example times bytes, and those do halve in float16.
skills: [memory]
''',
)

mcq(
    "mcq-what-dominates-memory",
    "A training run fits in GPU memory at a batch of 32 and runs out at 64. Which part of the memory grew?",
    [
        "The weights: a bigger batch needs more of them",
        "The optimizer state, which keeps a copy of the moments for every example in the batch",
        "The gradients, which are computed separately for every example in the batch and only averaged at the end of the step, so a bigger batch keeps more of them",
        "The activations: every layer's output is kept per example for the backward pass, so they scale with the batch; the weights and state don't",
    ],
    3,
    "The weights, the gradients and the optimizer moments are one copy each, whatever the batch; they are a fixed cost. The activations are kept per example, so doubling the batch doubles them, and at large batches they are most of the memory. A smaller batch, recomputing activations during the backward pass, or float16 activations are the usual ways back under the limit.",
    ["memory"],
)

mcq(
    "mcq-what-mixed-precision-trades",
    "What does mixed precision training keep in float32, what does it run in float16, and what does it gain?",
    [
        "Everything in float16, for half the memory of the whole run including the optimizer state; it gains speed at the cost of accuracy, which is why it is used only for inference and never for training",
        "Weights in float16 and activations in float32, since the activations are where precision matters",
        "Master weights and optimizer moments in float32, matrix multiplies and activations in float16; halved activation memory and a faster multiply, with loss scaling or bfloat16 for the range",
        "Float32 on the CPU and float16 on the GPU, so that data crosses the bus at half the size",
    ],
    2,
    "The float32 master copy of the weights and the optimizer state is what keeps small updates from being lost to float16's 11 significant bits; the matrix multiplies and the stored activations go to float16, where the memory and the tensor-core speed are. The state therefore stays about 16 bytes per parameter; the savings are in activations and traffic, and the risk is float16's narrow range, handled by scaling the loss or by bfloat16.",
    ["memory"],
)

mcq(
    "mcq-why-the-estimate-is-optimistic",
    "A run of 4.2 × 10²² FLOPs on a 10 TFLOP/s GPU is estimated at 133 years from the peak rate. In which direction is the estimate wrong, and why?",
    [
        "Too long: the peak rate is a minimum, and a well-written training loop exceeds it",
        "Too long: the estimate counts the backward pass, which the GPU does for free alongside the forward",
        "About right: the peak rate is what a GPU delivers on matrix multiplies, which are all a training step does once the data is on the device, so the only correction is the time to load it",
        "Too short: a loop sustains perhaps 30 to 50 percent of peak, because of memory-bound steps, small multiplies, data loading, Python glue and gradient exchange",
    ],
    3,
    "The spec-sheet rate assumes every arithmetic unit is busy every cycle. A real step has elementwise work that waits on memory, matrix multiplies too small to fill the chip, batches to load and move, Python glue, and on a cluster the averaging of gradients; the fraction of peak that survives all that is the utilization, and 30 to 50 percent is a good run. The backward pass costs twice the forward and is in the count; nothing is free.",
    ["time"],
)

mcq(
    "review-mcq-fits-on-the-gpu",
    "Can a network of a billion parameters be trained on a GPU with 24 GB of memory? Can it run?",
    [
        "Neither: a billion parameters is 4 GB in float32, and a GPU needs ten times the weights free to run anything",
        "It runs (2 GB in float16); training with Adam needs 16 GB of state before activations, so only with a tiny batch, a lighter optimizer, recomputation or sharding",
        "Both easily: the weights are 4 GB, which leaves 20 GB for everything else",
        "It trains but can't run, because inference needs the activations of the whole dataset at once, while training only ever needs one batch of them and the four copies of the weights",
    ],
    1,
    "Running needs the weights and one example's activations: 2 or 4 GB, which fits with room to spare. Training with Adam keeps four copies of the parameters, 16 GB, and then needs the activations of a batch, so 24 GB is too tight for a useful batch unless the state is shrunk (an 8-bit optimizer, fewer trained parameters), the activations are recomputed instead of stored, or the state is spread over several GPUs.",
    ["memory"],
)

mcq(
    "review-mcq-twice-the-tokens",
    "A 7-billion-parameter model on a trillion tokens is 4.2 × 10²² FLOPs, about 122 days on 1,000 GPUs of 10 TFLOP/s at 40 percent. The team decides to train on two trillion tokens instead. Roughly how long?",
    [
        "About 122 days: the model is the same size, and the parameters are what cost FLOPs; the tokens only decide how good it gets",
        "About 488 days: the cost grows with the square of the data",
        "About 244 days: training FLOPs are 6 times parameters times tokens, linear in the tokens",
        "About 61 days: more data makes each step more informative, so fewer steps are needed",
    ],
    2,
    "Every token costs about 6 FLOPs per parameter, forward and backward, so the run's cost is linear in the tokens as it is in the parameters. Doubling either doubles the FLOPs and, at the same utilization, the time. Whether the extra tokens are worth it is the scaling-law question; what they cost is just arithmetic.",
    ["time"],
)

write(
    "recall/review-predict-wider-and-deeper.yaml",
    f'''id: review-predict-wider-and-deeper
type: predict_output
rev: 1
prompt: |
  The parameters of a network, of the same network with its hidden layer doubled in width, and of the same network with a second hidden layer of the same width. What does the program print?
code: |
{block(REVIEW_WIDER)}expected_output: |
{block(REVIEW_WIDER_OUT)}explanation: |
  The narrow network is 100 times 100 plus 100, then 100 times 10 plus 10: 11,110. Doubling the hidden width doubles both layers that touch it: 20,200 plus 2,010. Adding a second hidden layer of 100 adds one more 100-by-100 block, 10,100, so deeper here costs almost the same as wider; widening a layer that sits between two wide layers would cost far more, since both of its blocks grow.
skills: [parameters]
''',
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-the-cost-of-a-network/exercise.yaml",
    f'''id: example-the-cost-of-a-network
stage: worked_example
rev: 1
title: "The cost of a network"
prompt: |
  A small network's parameters, the FLOPs of its forward and backward passes for one example and a batch, its bytes as weights, as training state and as activations at two precisions, and the time of an epoch and of a much larger run on a GPU of round numbers. Press **Run**, then read how each part works.
steps:
  - label: "Parameters and the forward pass"
    lines: "{ln('LAYERS = [784')}-{ln('a forward pass is')}"
    note: "Each dense layer is `in * out` weights and `out` biases: 200,960 plus 32,896 plus 1,290 is 235,146. The forward pass multiplies and adds once per weight for each example, so it is 2 FLOPs per parameter, 469,504 here; the biases and the activation functions aren't worth counting beside the matrix multiplies."
  - label: "The backward pass, and a batch"
    lines: "{ln('backward = 2 * forward')}-{ln('(forward + backward) * batch')}"
    note: "Going backward, each layer needs a gradient for its inputs and one for its weights, two matrix multiplies the size of the forward one: about twice the forward. A training step is therefore about 6 FLOPs per parameter per example, 1,408,512 here, and a batch of 64 is 64 times that."
  - label: "Bytes: weights, activations, state"
    lines: "{ln('weights in float32')}-{ln('training state with Adam')}"
    note: "Weights are parameters times bytes per value: 940,584 in float32, half in float16. Activations are every layer's output kept for the backward pass, per example, so a batch of 64 is 64 times 1,178 values; they halve in float16. Training state with Adam is four copies of the parameters, 16 bytes each in float32, and mixed precision's float32 master copy keeps that at 16: it saves on activations and speed, not on state."
  - label: "Time, and why the estimate is optimistic"
    lines: "{ln('GPU = 10e12')}-{ln('a 7 billion parameter model')}"
    note: "An epoch is 6 times the parameters times the examples: 8.5 × 10¹⁰ FLOPs, 8.5 ms at the round-number GPU's full 10 TFLOP/s and 28 ms at a realistic 30 percent, since memory-bound steps, small matrix multiplies, data loading and Python glue all leave the arithmetic units idle. The same arithmetic for a 7-billion-parameter model on a trillion tokens is 4.2 × 10²² FLOPs: 133 years on that GPU, four months on a thousand of them."
''',
)
write("exercises/example-the-cost-of-a-network/solution.py", EXAMPLE)
write(
    "exercises/example-the-cost-of-a-network/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the parameters, the three FLOP counts, the three byte counts and the two time estimates."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-training-bytes/exercise.yaml",
    f'''id: fill-training-bytes
stage: fill_in
rev: 1
title: "Bytes for a training run"
prompt: |
  `training_bytes(params, batch, activations_per_example, itemsize)` should add up the training state (weights, gradients and Adam's two moments: four copies of the parameters at `itemsize` bytes each) and the activations of one batch (`batch` examples, each `activations_per_example` values at `itemsize` bytes). Replace each `...` so the program prints the bytes for the small network at a batch of 64, then the gigabytes for a billion-parameter network at a batch of 8 with two million activations per example:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "Weights, gradients, first moment, second moment: four arrays the size of the parameters."
  - "The activations are per example, so the batch multiplies them."
skills: [memory]
''',
)
write("exercises/fill-training-bytes/starter.py", FILL_STARTER)
write("exercises/fill-training-bytes/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-training-bytes/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the two totals."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_more_values():
    """A batch of 0 is 16 bytes per parameter in float32 and 8 in float16, and activations add batch times values times bytes."""
    training_bytes = function("training_bytes")
    assert training_bytes(1000, 0, 500, 4) == 16000 and training_bytes(1000, 0, 500, 2) == 8000
    assert training_bytes(1000, 10, 500, 4) == 16000 + 20000
''',
)
write("exercises/fill-training-bytes/wrong/one-copy.py", FILL_WRONG)
write(
    "exercises/fill-training-bytes/wrong/typed-in.py",
    "def training_bytes(params, batch, activations_per_example, itemsize):\n    return 4063904\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-count-a-network/exercise.yaml",
    f'''id: write-count-a-network
stage: write
rev: 1
title: "Count a network"
prompt: |
  Write `parameter_count(layers)`, the weights and biases of every dense layer in a network given as a list of layer sizes (`[784, 256, 128, 10]` is three layers: 784 to 256, 256 to 128, 128 to 10), and `training_flops(layers, examples)`, the FLOPs of training on that many examples: a forward pass of 2 per weight per example and a backward pass of twice that, so three times the forward. Then print:

  ```python
  LAYERS = [784, 256, 128, 10]
  print(parameter_count(LAYERS), training_flops(LAYERS, 60_000))
  print(parameter_count([4, 3, 2]), training_flops([4, 3, 2], 10))
  ```

  ```
{block(WRITE_OUT)}  ```
hints:
  - "`zip(layers, layers[1:])` pairs each layer size with the next: the (in, out) of each dense layer."
  - "Biases count as parameters but not as FLOPs worth counting; the FLOPs are 2 per weight, times 3 for forward and backward, times the examples."
skills: [parameters, flops]
''',
)
write("exercises/write-count-a-network/starter.py", "")
write("exercises/write-count-a-network/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-count-a-network/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the two counts for both networks."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_edge_cases():
    """A single layer, a network with no layers, and the FLOPs of one example."""
    parameter_count = function("parameter_count")
    training_flops = function("training_flops")
    assert parameter_count([5, 1]) == 6 and parameter_count([7]) == 0
    assert training_flops([5, 1], 1) == 30 and training_flops([10, 10, 10], 100) == 3 * 400 * 100
''',
)
write("exercises/write-count-a-network/wrong/no-biases.py", WRITE_NO_BIAS)
write("exercises/write-count-a-network/wrong/forward-only.py", WRITE_FORWARD_ONLY)
write(
    "exercises/write-count-a-network/wrong/typed-in.py",
    "def parameter_count(layers):\n    return 235146\n\n\ndef training_flops(layers, examples):\n    return 84510720000\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-a-cost-calculator/exercise.yaml",
    f'''id: build-a-cost-calculator
stage: build
rev: 1
title: "A cost calculator"
prompt: |
  Starting from a blank editor, write five functions:

  - `parameter_count(layers)`: weights and biases of every dense layer, for a network given as a list of layer sizes.
  - `forward_flops(layers)`: a multiply and an add per weight, for one example.
  - `training_flops(layers, examples)`: forward plus a backward pass of twice the forward, for every example.
  - `training_bytes(params, batch, activations_per_example, itemsize)`: four copies of the parameters (weights, gradients, two Adam moments) plus one batch of activations, all at `itemsize` bytes per value.
  - `training_seconds(flops, flop_rate, utilization)`: the FLOPs over the rate the machine really sustains, its peak times the utilization.

  Then print:

  ```python
  LAYERS = [784, 256, 128, 10]
  print(parameter_count(LAYERS), forward_flops(LAYERS), training_flops(LAYERS, 60_000))
  print(training_bytes(parameter_count(LAYERS), 64, sum(LAYERS), 4), training_bytes(10**9, 8, 2 * 10**6, 2))
  print(round(training_seconds(training_flops(LAYERS, 60_000), 10e12, 1.0), 4), round(training_seconds(training_flops(LAYERS, 60_000), 10e12, 0.3), 4))
  print(round(training_seconds(6 * 7e9 * 1e12, 1000 * 10e12, 0.4) / 86400, 1))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks count tiny networks by hand, including one with a single layer and one with none, compare the FLOPs at two example counts, test the bytes at a batch of 0 and at both precisions, and check that halving the utilization doubles the time.
skills: [parameters, flops, memory, time]
''',
)
write("exercises/build-a-cost-calculator/starter.py", "")
write("exercises/build-a-cost-calculator/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-a-cost-calculator/test_exercise.py",
    f'''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the four lines."""
    assert run() == {BUILD_OUT!r}


def test_counts_by_hand():
    """[4, 3, 2] is 23 parameters and 36 forward FLOPs; [5, 1] is 6 and 10; [7] is 0 and 0."""
    parameter_count = function("parameter_count")
    forward_flops = function("forward_flops")
    assert parameter_count([4, 3, 2]) == 23 and forward_flops([4, 3, 2]) == 36
    assert parameter_count([5, 1]) == 6 and forward_flops([5, 1]) == 10
    assert parameter_count([7]) == 0 and forward_flops([7]) == 0


def test_training_flops():
    """Three times the forward pass per example, linear in the examples."""
    forward_flops = function("forward_flops")
    training_flops = function("training_flops")
    assert training_flops([4, 3, 2], 1) == 3 * forward_flops([4, 3, 2])
    assert training_flops([10, 20, 5], 200) == 2 * training_flops([10, 20, 5], 100)


def test_bytes():
    """A batch of 0 is 16 bytes per parameter in float32 and 8 in float16; activations add batch times values times bytes."""
    training_bytes = function("training_bytes")
    assert training_bytes(1000, 0, 500, 4) == 16000 and training_bytes(1000, 0, 500, 2) == 8000
    assert training_bytes(1000, 10, 500, 4) == 16000 + 20000


def test_seconds():
    """At full utilization the time is FLOPs over the peak; halving the utilization doubles it."""
    training_seconds = function("training_seconds")
    assert abs(training_seconds(1e12, 1e12, 1.0) - 1.0) < 1e-9
    assert abs(training_seconds(1e12, 1e12, 0.5) - 2.0) < 1e-9
''',
)
write("exercises/build-a-cost-calculator/wrong/no-biases.py", BUILD_NO_BIAS)
write("exercises/build-a-cost-calculator/wrong/forward-twice.py", BUILD_FORWARD_TWICE)
write("exercises/build-a-cost-calculator/wrong/one-copy.py", BUILD_ONE_COPY)
write("exercises/build-a-cost-calculator/wrong/times-utilization.py", BUILD_TIMES_UTILIZATION)
write(
    "exercises/build-a-cost-calculator/wrong/typed-in.py",
    "def parameter_count(layers):\n    return 235146\n\n\ndef forward_flops(layers):\n    return 469504\n\n\ndef training_flops(layers, examples):\n    return 84510720000\n\n\ndef training_bytes(params, batch, activations_per_example, itemsize):\n    return 4063904\n\n\ndef training_seconds(flops, flop_rate, utilization):\n    return 0.0085\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-count-and-an-estimate/exercise.yaml",
    f'''id: debug-a-count-and-an-estimate
stage: debug
rev: 1
title: "A count and an estimate"
prompt: |
  `parameter_count` should count the small network's weights and biases, and `training_seconds` should estimate an epoch on a 10 TFLOP/s GPU at 30 percent utilization. The program should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the count is `234,752`, 394 short, because the biases are left out; each layer has `out` of them on top of its `in * out` weights. And the epoch comes out at `2.5 ms` instead of `28.2`: the utilization is **multiplied** in, making the machine faster, when it should scale the peak rate **down**; the time is the FLOPs over peak times utilization.
skills: [parameters, time]
''',
)
write("exercises/debug-a-count-and-an-estimate/starter.py", DEBUG_STARTER)
write("exercises/debug-a-count-and-an-estimate/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-count-and-an-estimate/test_exercise.py",
    f'''from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the right count and the right estimate."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_other_values():
    """[4, 3, 2] has 23 parameters, and halving the utilization doubles the time."""
    parameter_count = function("parameter_count")
    training_seconds = function("training_seconds")
    assert parameter_count([4, 3, 2]) == 23
    assert abs(training_seconds(1e12, 1e12, 0.5) - 2 * training_seconds(1e12, 1e12, 1.0)) < 1e-9
''',
)
write("exercises/debug-a-count-and-an-estimate/wrong/still-no-biases.py", DEBUG_STILL_BIAS)
write("exercises/debug-a-count-and-an-estimate/wrong/still-times-utilization.py", DEBUG_STILL_UTILIZATION)
write(
    "exercises/debug-a-count-and-an-estimate/wrong/typed-in.py",
    "def parameter_count(layers):\n    return 235146\n\n\ndef training_seconds(flops, flop_rate, utilization):\n    return 0.0282\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-count-from-memory/exercise.yaml",
    f'''id: review-count-from-memory
stage: review_code
rev: 1
title: "Parameters, from memory"
prompt: |
  Write `parameter_count(layers)`, the weights and biases of every dense layer of a network given as a list of layer sizes, and print it for `[784, 256, 128, 10]` and for `[4, 3, 2]`:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [parameters]
''',
)
write("exercises/review-count-from-memory/starter.py", "")
write("exercises/review-count-from-memory/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-count-from-memory/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the two counts."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_more_networks():
    """A single layer from 5 to 1 is 6 parameters; a list with one size is 0."""
    parameter_count = function("parameter_count")
    assert parameter_count([5, 1]) == 6 and parameter_count([9]) == 0
''',
)
write("exercises/review-count-from-memory/wrong/no-biases.py", REVIEW_CODE_WRONG)
write(
    "exercises/review-count-from-memory/wrong/typed-in.py",
    "def parameter_count(layers):\n    return 235146\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.hw.cost-of-a-model written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
