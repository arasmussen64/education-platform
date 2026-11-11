"""Writes the topic ml.hw.parallelism-and-gpus (Module 7's fifth topic). Run
from the repository root under uv (python -m uv run python <this file>), so
every program's expected output is captured from CPython rather than typed
in. There is no GPU in the browser, so everything is counted: Amdahl's law,
the FLOPs and bytes of a matrix multiply, a roofline of round numbers, and
the cost of moving data across the bus. Files are written as bytes with LF
endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.hw.parallelism-and-gpus")


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

EXAMPLE = '''import math


def speedup(parallel_fraction, workers):
    """Amdahl's law: the serial part keeps its whole time; only the parallel part is shared out."""
    serial = 1 - parallel_fraction
    return 1 / (serial + parallel_fraction / workers)


for p in (0.5, 0.9, 0.99):
    print(f"{p:.0%} parallel:", " ".join(f"{workers} workers {speedup(p, workers):.1f}x" for workers in (2, 8, 64, 1000)), f"| limit {1 / (1 - p):.0f}x")

items = 1_000_000
print(f"{items:,} independent items on 8 workers: {math.ceil(items / 8):,} steps each | a chain of {items:,} dependent steps on 8 workers: {items:,} steps")


def matmul_cost(m, k, n, itemsize=4):
    """FLOPs and bytes of (m, k) @ (k, n): a multiply and an add for each of the k terms of each of the m * n outputs; read both inputs, write the output."""
    flops = 2 * m * k * n
    bytes_moved = (m * k + k * n + m * n) * itemsize
    return flops, bytes_moved


flops, bytes_moved = matmul_cost(1024, 1024, 1024)
print(f"1024 x 1024 @ 1024 x 1024 in float32: {flops:,} FLOPs, {bytes_moved:,} bytes, {flops / bytes_moved:.0f} FLOPs per byte")
add_flops, add_bytes = 1_000_000, 3 * 1_000_000 * 4
print(f"adding two vectors of a million float32: {add_flops:,} FLOPs, {add_bytes:,} bytes, {add_flops / add_bytes:.2f} FLOPs per byte")

FLOP_RATE, BANDWIDTH = 10e12, 500e9
print(f"a GPU of round numbers, 10 TFLOP/s and 500 GB/s, does {FLOP_RATE / BANDWIDTH:.0f} FLOPs per byte it fetches: above that compute-bound, below it memory-bound")
for name, (f, b) in (("the matrix multiply", (flops, bytes_moved)), ("the vector add", (add_flops, add_bytes))):
    compute, memory = f / FLOP_RATE, b / BANDWIDTH
    print(f"{name}: {compute * 1e6:.1f} us of arithmetic, {memory * 1e6:.1f} us of memory traffic, so it is {'compute' if compute > memory else 'memory'}-bound")

k, n = 1024, 1024
print("FLOPs per byte of (batch, 1024) @ (1024, 1024), the weights read once per batch:", " ".join(f"batch {b}: {matmul_cost(b, k, n)[0] / matmul_cost(b, k, n)[1]:.1f}" for b in (1, 8, 64, 512)))

BUS, LATENCY = 25e9, 10e-6
dataset = 1_000_000_000
print(f"moving a 1 GB dataset to the GPU once: {dataset / BUS * 1000:.0f} ms | as a million 1 KB pieces: {dataset / BUS + 1_000_000 * LATENCY:.0f} s, almost all of it the fixed cost per transfer")
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert len(EX) == 11, EX
assert EX[0] == "50% parallel: 2 workers 1.3x 8 workers 1.8x 64 workers 2.0x 1000 workers 2.0x | limit 2x", EX[0]
assert EX[1] == "90% parallel: 2 workers 1.8x 8 workers 4.7x 64 workers 8.8x 1000 workers 9.9x | limit 10x", EX[1]
assert EX[2] == "99% parallel: 2 workers 2.0x 8 workers 7.5x 64 workers 39.3x 1000 workers 91.0x | limit 100x", EX[2]
assert EX[3] == "1,000,000 independent items on 8 workers: 125,000 steps each | a chain of 1,000,000 dependent steps on 8 workers: 1,000,000 steps", EX[3]
assert EX[4] == "1024 x 1024 @ 1024 x 1024 in float32: 2,147,483,648 FLOPs, 12,582,912 bytes, 171 FLOPs per byte", EX[4]
assert EX[5] == "adding two vectors of a million float32: 1,000,000 FLOPs, 12,000,000 bytes, 0.08 FLOPs per byte", EX[5]
assert EX[6].startswith("a GPU of round numbers, 10 TFLOP/s and 500 GB/s, does 20 FLOPs per byte"), EX[6]
assert EX[7] == "the matrix multiply: 214.7 us of arithmetic, 25.2 us of memory traffic, so it is compute-bound", EX[7]
assert EX[8] == "the vector add: 0.1 us of arithmetic, 24.0 us of memory traffic, so it is memory-bound", EX[8]
assert EX[9].endswith("batch 1: 0.5 batch 8: 3.9 batch 64: 28.4 batch 512: 128.0"), EX[9]
assert EX[10] == "moving a 1 GB dataset to the GPU once: 40 ms | as a million 1 KB pieces: 10 s, almost all of it the fixed cost per transfer", EX[10]
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_AMDAHL = '''def speedup(parallel_fraction, workers):
    return 1 / ((1 - parallel_fraction) + parallel_fraction / workers)


print(round(speedup(0.5, 2), 2), round(speedup(0.5, 1000), 2))
print(round(speedup(0.95, 20), 2), round(speedup(1.0, 20), 2))
'''
PREDICT_AMDAHL_OUT = out(PREDICT_AMDAHL)
assert PREDICT_AMDAHL_OUT == "1.33 2.0\n10.26 20.0\n", PREDICT_AMDAHL_OUT

PREDICT_MATMUL = '''def matmul_cost(m, k, n, itemsize):
    return 2 * m * k * n, (m * k + k * n + m * n) * itemsize


print(matmul_cost(2, 3, 4, 8))
flops, bytes_moved = matmul_cost(256, 256, 256, 4)
print(flops, bytes_moved, flops // bytes_moved)
'''
PREDICT_MATMUL_OUT = out(PREDICT_MATMUL)
assert PREDICT_MATMUL_OUT == "(48, 208)\n33554432 786432 42\n", PREDICT_MATMUL_OUT

REVIEW_INTENSITY = '''n, itemsize = 1_000_000, 4
add = (n, 3 * n * itemsize)
scale_in_place = (n, 2 * n * itemsize)
dot = (2 * n, 2 * n * itemsize)
for name, (flops, bytes_moved) in (("add", add), ("scale in place", scale_in_place), ("dot", dot)):
    print(name, round(flops / bytes_moved, 3))
print("ridge of a 10 TFLOP/s, 500 GB/s machine:", 10e12 / 500e9)
'''
REVIEW_INTENSITY_OUT = out(REVIEW_INTENSITY)
assert REVIEW_INTENSITY_OUT == "add 0.083\nscale in place 0.125\ndot 0.25\nridge of a 10 TFLOP/s, 500 GB/s machine: 20.0\n", REVIEW_INTENSITY_OUT

PARSONS_LINES = [
    "def speedup(parallel_fraction, workers):",
    "    serial = 1 - parallel_fraction",
    "    return 1 / (serial + parallel_fraction / workers)",
    "print(round(speedup(0.9, 1000), 1))",
]
assert out("\n".join(PARSONS_LINES) + "\n") == "9.9\n"
assert out("\n".join(PARSONS_LINES).replace("parallel_fraction / workers", "parallel_fraction * workers") + "\n") != "9.9\n"

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''def arithmetic_intensity(m, k, n, itemsize):
    """FLOPs per byte of (m, k) @ (k, n): two operations per term of each output, over the bytes of both inputs and the output."""
    flops = 2 * m * k * n
    bytes_moved = (m * k + k * n + m * n) * itemsize
    return flops / bytes_moved


print(round(arithmetic_intensity(1024, 1024, 1024, 4), 1))
print(round(arithmetic_intensity(1, 1024, 1024, 4), 1), round(arithmetic_intensity(64, 1024, 1024, 4), 1))
'''
FILL_STARTER = FILL_SOLUTION.replace("    flops = 2 * m * k * n\n", "    flops = ... * m * k * n\n").replace("    bytes_moved = (m * k + k * n + m * n) * itemsize\n", "    bytes_moved = (m * k + ... + m * n) * itemsize\n")
FILL_WRONG = FILL_SOLUTION.replace("    flops = 2 * m * k * n\n", "    flops = m * k * n\n")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "170.7\n0.5 28.4\n", FILL_OUT
assert out(FILL_WRONG) != FILL_OUT

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''def speedup(parallel_fraction, workers):
    """Amdahl's law: the serial part is untouched, the parallel part is divided by the workers."""
    return 1 / ((1 - parallel_fraction) + parallel_fraction / workers)


def roofline_seconds(flops, bytes_moved, flop_rate, bandwidth):
    """The time a machine needs for the arithmetic or for the bytes, whichever is longer: it overlaps the two."""
    return max(flops / flop_rate, bytes_moved / bandwidth)


print(round(speedup(0.9, 8), 2), round(speedup(0.9, 10**6), 2))
print(round(roofline_seconds(2 * 1024**3, 3 * 1024**2 * 4, 10e12, 500e9) * 1e6, 1))
print(round(roofline_seconds(1_000_000, 12_000_000, 10e12, 500e9) * 1e6, 1))
'''
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "4.71 10.0\n214.7\n24.0\n", WRITE_OUT
WRITE_SUMMED = WRITE_SOLUTION.replace("    return max(flops / flop_rate, bytes_moved / bandwidth)", "    return flops / flop_rate + bytes_moved / bandwidth")
WRITE_INVERTED = WRITE_SOLUTION.replace("    return 1 / ((1 - parallel_fraction) + parallel_fraction / workers)", "    return 1 / (parallel_fraction + (1 - parallel_fraction) / workers)")
assert out(WRITE_SUMMED) != WRITE_OUT and out(WRITE_INVERTED) != WRITE_OUT

# --- the build ----------------------------------------------------------------------------------

BUILD_SOLUTION = '''def amdahl(parallel_fraction, workers):
    """The speed-up Amdahl's law allows: the serial part keeps its time, the parallel part is shared."""
    return 1 / ((1 - parallel_fraction) + parallel_fraction / workers)


def matmul_cost(m, k, n, itemsize):
    """(FLOPs, bytes) of (m, k) @ (k, n): a multiply and an add per term, both inputs read and the output written once."""
    return 2 * m * k * n, (m * k + k * n + m * n) * itemsize


def intensity(flops, bytes_moved):
    """FLOPs per byte."""
    return flops / bytes_moved


def roofline_seconds(flops, bytes_moved, flop_rate, bandwidth):
    """The longer of the arithmetic time and the memory time, since the machine overlaps them."""
    return max(flops / flop_rate, bytes_moved / bandwidth)


def transfer_seconds(total_bytes, pieces, bandwidth, latency):
    """Moving total_bytes across a bus in that many pieces: the bytes at the bandwidth, plus a fixed latency per piece."""
    return total_bytes / bandwidth + pieces * latency


print(round(amdahl(0.9, 8), 2), round(amdahl(0.9, 10**9), 2), round(amdahl(0.99, 64), 1))
print(matmul_cost(1024, 1024, 1024, 4), round(intensity(*matmul_cost(1024, 1024, 1024, 4)), 1))
print(round(intensity(*matmul_cost(1, 1024, 1024, 4)), 2), round(intensity(*matmul_cost(512, 1024, 1024, 4)), 1))
print(round(roofline_seconds(*matmul_cost(1024, 1024, 1024, 4), 10e12, 500e9) * 1e6, 1), round(roofline_seconds(1_000_000, 12_000_000, 10e12, 500e9) * 1e6, 1))
print(round(transfer_seconds(10**9, 1, 25e9, 10e-6), 3), round(transfer_seconds(10**9, 10**6, 25e9, 10e-6), 2))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == "4.71 10.0 39.3\n(2147483648, 12582912) 170.7\n0.5 128.0\n214.7 24.0\n0.04 10.04\n", BUILD_OUT
BUILD_INVERTED = BUILD_SOLUTION.replace("    return 1 / ((1 - parallel_fraction) + parallel_fraction / workers)", "    return 1 / (parallel_fraction + (1 - parallel_fraction) / workers)")
BUILD_HALF_FLOPS = BUILD_SOLUTION.replace("    return 2 * m * k * n, (m * k + k * n + m * n) * itemsize", "    return m * k * n, (m * k + k * n + m * n) * itemsize")
BUILD_SUMMED = BUILD_SOLUTION.replace("    return max(flops / flop_rate, bytes_moved / bandwidth)", "    return flops / flop_rate + bytes_moved / bandwidth")
BUILD_NO_LATENCY = BUILD_SOLUTION.replace("    return total_bytes / bandwidth + pieces * latency", "    return total_bytes / bandwidth")
for wrong in (BUILD_INVERTED, BUILD_HALF_FLOPS, BUILD_SUMMED, BUILD_NO_LATENCY):
    assert wrong != BUILD_SOLUTION and out(wrong) != BUILD_OUT

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''def amdahl(parallel_fraction, workers):
    """The speed-up from sharing the parallel part among the workers; the serial part keeps its whole time."""
    serial = 1 - parallel_fraction
    return 1 / (serial + parallel_fraction / workers)


def matmul_cost(m, k, n, itemsize):
    """(FLOPs, bytes) of (m, k) @ (k, n): each of the m * n outputs sums k products, a multiply and an add each."""
    flops = 2 * m * k * n
    bytes_moved = (m * k + k * n + m * n) * itemsize
    return flops, bytes_moved


print(f"8 workers on 90% parallel work: {amdahl(0.9, 8):.2f}x")
flops, bytes_moved = matmul_cost(1024, 1024, 1024, 4)
print(f"1024-cube matmul: {flops:,} FLOPs, {bytes_moved:,} bytes, {flops / bytes_moved:.1f} FLOPs per byte")
'''
BUG_SWAPPED = ("    return 1 / (serial + parallel_fraction / workers)", "    return 1 / (parallel_fraction + serial / workers)")
BUG_HALF = ("    flops = 2 * m * k * n", "    flops = m * k * n")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_SWAPPED).replace(*BUG_HALF)
DEBUG_STILL_SWAPPED = DEBUG_SOLUTION.replace(*BUG_SWAPPED)
DEBUG_STILL_HALF = DEBUG_SOLUTION.replace(*BUG_HALF)
DEBUG_OUT = out(DEBUG_SOLUTION)
STARTER_OUT = out(DEBUG_STARTER)
print("debug:\n" + DEBUG_OUT + "starter:\n" + STARTER_OUT)
assert DEBUG_OUT == "8 workers on 90% parallel work: 4.71x\n1024-cube matmul: 2,147,483,648 FLOPs, 12,582,912 bytes, 170.7 FLOPs per byte\n", DEBUG_OUT
assert STARTER_OUT == "8 workers on 90% parallel work: 1.10x\n1024-cube matmul: 1,073,741,824 FLOPs, 12,582,912 bytes, 85.3 FLOPs per byte\n", STARTER_OUT
assert out(DEBUG_STILL_SWAPPED) != DEBUG_OUT and out(DEBUG_STILL_HALF) != DEBUG_OUT

REVIEW_CODE_SOLUTION = '''def speedup(parallel_fraction, workers):
    """Amdahl's law."""
    return 1 / ((1 - parallel_fraction) + parallel_fraction / workers)


print(round(speedup(0.8, 4), 2), round(speedup(0.8, 64), 2), round(speedup(0.8, 10**9), 2))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "2.5 4.71 5.0\n", REVIEW_CODE_OUT
REVIEW_CODE_WRONG = REVIEW_CODE_SOLUTION.replace("    return 1 / ((1 - parallel_fraction) + parallel_fraction / workers)", "    return 1 / (parallel_fraction + (1 - parallel_fraction) / workers)")
assert out(REVIEW_CODE_WRONG) != REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.hw.parallelism-and-gpus
kind: topic
status: ready
title: "Parallelism and what a GPU is good at"
summary: "Cores and threads, work that splits and work that doesn't, Amdahl's law computed, a GPU as thousands of simple cores doing the same operation on different data, memory bandwidth as the usual limit, and why a matrix multiply is the operation GPUs were built for."
prerequisites: [ml.hw.vectorization]
estimated_minutes: 50
rev: 1
objectives:
  - "Tell data parallelism from a sequential dependence, and compute the speed-up Amdahl's law allows."
  - "Explain what a GPU is: many simple cores running the same instruction on different data, with its own memory."
  - "Count the operations and the bytes of a matrix multiply, and say why its arithmetic intensity suits a GPU."
  - "Say what memory bandwidth limits, why batches help, and what moving data between CPU and GPU costs."
# Linked, never copied or embedded: Wikipedia is CC BY-SA 4.0.
resources:
  - title: "Wikipedia: Amdahl's law (the formula, the derivation and the graph of speed-up against workers)"
    url: https://en.wikipedia.org/wiki/Amdahl%27s_law
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
  - title: "Wikipedia: Graphics processing unit (the Computational functions and GPU forms sections: what the hardware is and how it differs from a CPU)"
    url: https://en.wikipedia.org/wiki/Graphics_processing_unit
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
  - title: "Wikipedia: Roofline model (arithmetic intensity, the ridge point, and compute-bound against memory-bound)"
    url: https://en.wikipedia.org/wiki/Roofline_model
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
practice:
  - example-amdahl-and-a-matrix-multiply
  - predict-amdahl
  - parsons-amdahl
  - mcq-what-a-gpu-is
  - mcq-which-work-suits-a-gpu
  - predict-matmul-counts
  - fill-arithmetic-intensity
  - mcq-why-batches-help
  - mcq-the-transfer
  - write-speedup-and-roofline
prove:
  build: build-a-parallel-cost-toolkit
  debug: debug-a-speed-up-and-a-count
  explain:
    prompt: |
      A teammate plans to run a data pipeline on a 64-core machine and expects it to be 64 times faster; another asks how a GPU can be faster than a CPU when its clock is slower; a third moved a model to the GPU, feeds it one example at a time, and finds it slower than the CPU was. In your own words: what work splits across workers and what doesn't, and what Amdahl's law says the first teammate will get if a tenth of the pipeline is serial; what a GPU is and what kind of work it is built for; how to count the operations and bytes of a matrix multiply and why its arithmetic intensity suits a GPU while an elementwise operation's doesn't; and why the third teammate's batch size and data transfers make the GPU slow.
    rubric:
      - id: amdahl
        required: true
        description: "Independent items split across workers (data parallelism); a chain where each step needs the last doesn't. Amdahl: speed-up is 1 over (serial fraction plus parallel fraction over workers), so with a tenth serial, 64 workers give about 8.8 times and no number of workers gives more than 10; the serial part (loading, Python glue, waiting) is what to shrink."
      - id: gpu
        required: true
        description: "A GPU is thousands of simple cores grouped to run the same instruction on different data at once, with a slower clock, little ability to branch independently, and its own memory with very high bandwidth. It is built for one operation over huge arrays, not for branchy or sequential or small work."
      - id: intensity
        required: true
        description: "(m, k) @ (k, n) is 2mkn FLOPs and (mk + kn + mn) times the item size in bytes, so a 1024-cube in float32 is about 171 FLOPs per byte: the arithmetic grows as the cube and the bytes as the square. An elementwise add is one FLOP per 12 bytes. A machine's ridge is its FLOP rate over its bandwidth (20 for 10 TFLOP/s and 500 GB/s); above it compute-bound, below it memory-bound."
      - id: bandwidth
        required: true
        description: "Below the ridge the GPU waits on memory however fast its arithmetic. A batch of 1 against a weight matrix is about 0.5 FLOPs per byte, memory-bound; a batch of 512 is 128, because the weights are read once per batch. Moving data across the bus costs the bytes at tens of gigabytes per second plus a fixed latency per transfer, so data moves once and stays on the device; per-example transfers are seconds of latency."
    model_answer: |
      Work splits across workers when its pieces don't depend on each other: a million independent rows on eight workers is 125,000 each. A chain where every step needs the result of the step before doesn't split; eight workers still take a million steps. Amdahl's law says what the splitting is worth: if a fraction p of the time is parallel and the rest serial, the speed-up on w workers is 1 over (1 minus p, plus p over w). With a tenth of the pipeline serial, 64 cores give 1 over (0.1 plus 0.9 over 64), about 8.8 times, and no number of cores gives more than 10, because the serial tenth is still there. So the first teammate gets nine times, not sixty-four, and the way to more is to shrink the serial part, which is usually data loading, Python glue between the parallel parts, and waiting for everyone to finish. A GPU is thousands of simple cores arranged in groups that run the same instruction on different data at the same time, each slower than a CPU core and far worse at branching, with its own memory whose bandwidth is many times a CPU's. That is why its clock doesn't matter: it is built to do one operation across a huge array, which is exactly what a vectorized step or a matrix multiply is, and it is bad at anything branchy, sequential or small. To count a matrix multiply, (m, k) times (k, n) does m times n outputs, each a sum of k products, so 2 m k n floating-point operations, and it reads both inputs and writes the output once, (m k plus k n plus m n) elements times the bytes per element. A 1024 by 1024 by 1024 multiply in float32 is about 2.1 billion FLOPs over 12.6 megabytes, about 171 FLOPs per byte, and the ratio grows with the size, since the arithmetic goes as the cube and the bytes as the square. Adding two vectors is one FLOP per 12 bytes, forever. A machine has a FLOP rate and a bandwidth, and their ratio, the ridge, is the intensity at which it is equally limited by both: 20 FLOPs per byte for a GPU of 10 TFLOP/s and 500 GB/s. The multiply sits far above the ridge, compute-bound, so the GPU's arithmetic is what counts; the add sits far below, memory-bound, so the GPU waits on memory and its arithmetic rate is irrelevant. The third teammate's problem is on the wrong side of the ridge. With one example at a time, the layer is a vector times a weight matrix, about half a FLOP per byte, because the whole weight matrix is read for one row's worth of arithmetic; at a batch of 512 the same weights are read once for 512 rows, 128 FLOPs per byte, and the GPU is busy. And each example that is moved to the GPU separately pays a fixed latency per transfer on top of the bytes: a million small transfers is seconds of latency for a gigabyte that would move in 40 milliseconds in one piece. Move the data once, keep it on the device, and batch.
review_pool:
  - review-mcq-serial-fraction
  - review-predict-intensity-of-elementwise
  - review-mcq-memory-bound-step
  - review-amdahl
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: amdahl
    description: "Tell data parallelism from a sequential dependence, and compute the speed-up Amdahl's law allows"
  - id: gpu
    description: "Explain what a GPU is and what work it is built for"
  - id: intensity
    description: "Count the FLOPs and bytes of a matrix multiply, and read its arithmetic intensity against a machine's ridge"
  - id: bandwidth
    description: "Say what bandwidth limits, why batches help, and what moving data across the bus costs"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    '''<Intro>

Why vectorized code is fast made each operation cheap; this one asks how many can run at once. A laptop has a handful of cores, a server dozens, a GPU thousands, and the question is always the same: which parts of the work can be shared out, and what is left over when they are. This topic computes **Amdahl's law**, says what a **GPU** is and what it is built for, counts the operations and bytes of a **matrix multiply** to show why it suits one, and ends with the two things that make a GPU slow in practice, a batch that is too small and data that keeps crossing the bus. There is no GPU in the browser, so everything here is counted.

The main resource is **Wikipedia's _Amdahl's law_ page**: the formula, where it comes from, and the graph of speed-up against workers that flattens out at one over the serial fraction; about 15 minutes. The _Graphics processing unit_ page says what the hardware is, and the _Roofline model_ page is where arithmetic intensity and the ridge point come from. Watch for:

- **The serial fraction**: the part of the time that no number of workers shortens.
- **Same instruction, different data**: the one thing a GPU does, thousands of times over.
- **Arithmetic intensity** and the **ridge point**: FLOPs (floating-point operations, one add or one multiply each) per byte, and the number a machine needs to stay busy.

</Intro>

<Resource index={0} />

<Recap>

- **What splits and what doesn't.** A **core** runs one stream of instructions, a **thread**, at the pace of its **clock**; more cores run more streams at once, if the work splits. A million independent rows on 8 workers is 125,000 each: **data parallelism**, the same operation on different pieces. A chain where each step needs the step before (the moving average from Why vectorized code is fast, a running state) doesn't split; 8 workers still take a million steps. Most programs are a mix, and the mix decides the gain.
- **Amdahl's law.** If a fraction `p` of the time is parallel, `w` workers give a speed-up of `1 / ((1 - p) + p / w)`. The serial part keeps its whole time, so the speed-up flattens at `1 / (1 - p)`: 90 percent parallel is 4.7 times on 8 workers, 8.8 on 64, and never more than 10; 99 percent reaches 91 on 1,000. To go faster with many workers, shrink the serial part: data loading, Python glue, waiting for the slowest worker, the moment when results are combined.
- **What a GPU is.** Thousands of simple cores, grouped so that each group runs the **same instruction on different data** at the same time (the SIMD idea at a much larger scale), with a slower clock than a CPU core, little ability to branch independently, and its **own memory** whose bandwidth is many times a CPU's. It is built for one operation over a huge array: a vectorized step, a matrix multiply, an image. It is bad at branchy code, sequential chains and small arrays, where most of its cores sit idle.
- **Counting a matrix multiply.** `(m, k) @ (k, n)` computes `m * n` outputs that are each a sum of `k` products: `2 * m * k * n` FLOPs (a multiply and an add per term). It reads both inputs and writes the output: `(m * k + k * n + m * n)` elements times the bytes each. A 1024-cube in float32 is 2,147,483,648 FLOPs over 12,582,912 bytes: **171 FLOPs per byte**, and the ratio grows with the size, because the arithmetic grows as the cube and the bytes as the square. Adding two vectors is 1 FLOP per 12 bytes, at any size.
- **The roofline** (the graph of the FLOP rate a machine can reach against arithmetic intensity: a slope up to the ridge, flat beyond it). A machine has a FLOP rate and a memory bandwidth; their ratio is its **ridge**, the arithmetic intensity at which it is equally limited by both. For a GPU of round numbers, 10 TFLOP/s (ten trillion floating-point operations a second) and 500 GB/s, the ridge is 20 FLOPs per byte (real ones sit at tens to a few hundred). Above it, time is `flops / rate`: **compute-bound**, the multiply at 215 microseconds. Below it, time is `bytes / bandwidth`: **memory-bound**, the vector add at 24 microseconds with the arithmetic taking 0.1. Time is the larger of the two, because the machine overlaps them. Outside the matrix multiplies, most of a training step is memory-bound, which is why fusing operations (one pass instead of three) is a speed-up, as Memory, caches and locality said.
- **Why batches help.** A layer is `(batch, k) @ (k, n)` and its weights are read once per batch. At a batch of 1 that is 0.5 FLOPs per byte, memory-bound: the whole weight matrix is fetched for one row of arithmetic. At 8 it is 3.9, at 64 it is 28 and over the ridge, at 512 it is 128. The same weights, the same per-row arithmetic, and the GPU is busy instead of waiting. Per-example inference is the classic way to make a GPU slower than a CPU.
- **Crossing the bus.** CPU and GPU memories are separate, joined by a bus of tens of gigabytes per second with a fixed latency (a wait before the first byte moves) per transfer. A gigabyte moves in about 40 milliseconds in one piece and in about 10 seconds as a million one-kilobyte pieces, almost all of it latency. Move data once, keep it on the device, do many steps there; a transfer inside the training loop, one example at a time, is the second classic mistake.
- **In machine learning** (names you'll meet later): **data-parallel training** runs the same model on a slice of the batch per GPU and averages the gradients, and the averaging is the serial part Amdahl charges for; **mixed precision** halves the bytes, which doubles the effective bandwidth for memory-bound steps; **tensor cores** are matrix-multiply units that raise the FLOP rate, and so the ridge; and a dashboard showing low "GPU utilization" means memory-bound, transfer-bound or batch too small, in that order of likelihood.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/predict-amdahl.yaml",
    f'''id: predict-amdahl
type: predict_output
rev: 1
prompt: |
  Amdahl's law for half-parallel work on 2 and on 1,000 workers, then 95 percent parallel on 20 and fully parallel on 20. What does the program print?
code: |
{block(PREDICT_AMDAHL)}expected_output: |
{block(PREDICT_AMDAHL_OUT)}explanation: |
  Half parallel: 2 workers give 1 over (0.5 plus 0.25), 1.33; a thousand workers give 1 over (0.5 plus 0.0005), which rounds to 2, the limit of 1 over the serial half. 95 percent parallel on 20 is 1 over (0.05 plus 0.0475), 10.26, about half of what 20 workers would give with no serial part at all; fully parallel work is the only case where the speed-up equals the worker count.
skills: [amdahl]
''',
)

write(
    "recall/parsons-amdahl.yaml",
    "id: parsons-amdahl\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to define Amdahl's law and print the speed-up of 90 percent parallel work on 1,000 workers, `9.9`. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("    return 1 / (serial + parallel_fraction * workers)")
    + "\nexplanation: |\n"
    + block("The parallel part is divided among the workers and the serial part is left as it is, so the total time is `serial + parallel_fraction / workers` and the speed-up is 1 over that: 1 over (0.1 plus 0.0009), 9.9. The decoy multiplies the parallel part by the workers, as if more workers made the work bigger, and gives a speed-up under 1.")
    + "skills: [amdahl]\n",
)

mcq(
    "mcq-what-a-gpu-is",
    "A GPU's cores run at a lower clock than a CPU's. How can it be faster at a matrix multiply?",
    [
        "Its cores are faster at floating point because they skip the rounding that a CPU does on every operation, which is most of the work",
        "It caches the result of every matrix multiply, so repeated training steps are free after the first one",
        "Thousands of simple cores run the same instruction on different data at once, beside memory of far higher bandwidth",
        "It compiles Python to machine code, which removes the interpreter overhead that the CPU pays on every element",
    ],
    2,
    "A GPU trades a few fast, flexible cores for thousands of slow, simple ones that work in lockstep, each group executing one instruction over many data elements, and pairs them with memory many times wider than a CPU's. A matrix multiply is the same operation over a huge array, so all of those cores are busy. The floating point is the same IEEE arithmetic, nothing is cached between steps, and the GPU doesn't run Python at all; a library sends it the whole operation.",
    ["gpu"],
)

mcq(
    "mcq-which-work-suits-a-gpu",
    "Which of these would a GPU speed up the most, and which the least?",
    [
        "Most: walking a binary search tree of a million nodes; least: a matrix multiply, which is too regular to parallelize",
        "Most: a Python loop over a dictionary; least: an elementwise operation on a huge array",
        "They are all the same, since a GPU speeds up every program by the ratio of its core count to the CPU's",
        "Most: a 4096-square matrix multiply; least: a loop whose every step depends on the previous step's result",
    ],
    3,
    "A GPU is built for one instruction over many data elements: a big matrix multiply keeps thousands of cores busy on independent outputs. A sequential chain is the opposite: one step at a time, with all but one core idle. Tree walks and dictionary loops branch at every node and run in Python, which the GPU doesn't execute; an elementwise operation on a huge array is a good fit, limited by memory bandwidth rather than by arithmetic.",
    ["gpu"],
)

write(
    "recall/predict-matmul-counts.yaml",
    f'''id: predict-matmul-counts
type: predict_output
rev: 1
prompt: |
  The FLOPs and bytes of a small matrix multiply in float64, and of a 256-cube in float32 with its FLOPs per byte. What does the program print?
code: |
{block(PREDICT_MATMUL)}expected_output: |
{block(PREDICT_MATMUL_OUT)}explanation: |
  `(2, 3) @ (3, 4)` makes 8 outputs of 3 terms each, 24 multiplies and 24 adds, 48 FLOPs; it reads 6 and 12 elements and writes 8, 26 elements of 8 bytes, 208 bytes. The 256-cube is 2 times 256 cubed, 33,554,432 FLOPs, over 3 times 256 squared elements of 4 bytes, 786,432 bytes: 42 FLOPs per byte, and a 1024-cube would be four times that, since the FLOPs grow as the cube and the bytes as the square.
skills: [intensity]
''',
)

mcq(
    "mcq-why-batches-help",
    "A layer multiplies its input by a `(1024, 1024)` weight matrix. Why does a batch of 256 examples take only a few times as long as a single example on a GPU, instead of 256 times?",
    [
        "Because the weights are read once per batch, so 256 rows of arithmetic share one fetch and the step crosses the ridge",
        "Because the GPU has exactly 256 cores, so a batch of 256 uses all of them and one example uses one",
        "Because the GPU caches the weights after the first example, so only the first example of a batch pays for them and the rest are free",
        "Because batching rounds the inputs to float16, which halves the arithmetic",
    ],
    0,
    "With one example, the whole 4-megabyte weight matrix is fetched to do one row's worth of multiplications: about half a FLOP per byte, far below the ridge, so the step waits on memory. With 256 rows the same fetch serves 256 rows of arithmetic, about 85 FLOPs per byte, above the ridge, and the arithmetic units are busy. The core count is in the thousands, nothing is cached between steps, and precision is a separate choice.",
    ["bandwidth"],
)

mcq(
    "mcq-the-transfer",
    "A training step takes 2 ms of GPU time but the loop runs at 30 ms per step. The loop copies each batch to the GPU inside the step and copies the loss back. What is the likely cause, and the fix?",
    [
        "The GPU is too slow for the model; a bigger GPU is needed",
        "Python's garbage collector runs between steps; disable it during training",
        "The model's weights are copied to the GPU on every step, which is what the 28 ms are; load the model once at the start and the step will take its 2 ms",
        "The copies across the bus, each paying bytes at bus speed plus a fixed latency; keep the data on the device and read results back rarely",
    ],
    3,
    "The step itself is fast; the time is in moving data. A batch across the bus costs its bytes at the bus bandwidth and a fixed latency for every transfer, and a loss copied back forces the loop to wait for the GPU before it continues. Loading the whole dataset to the device once, or at least prefetching the next batch while the current one runs, and reading the loss back every hundred steps, removes most of it. The weights are already on the device; a faster GPU would make the 2 ms smaller and leave the 28.",
    ["bandwidth"],
)

mcq(
    "review-mcq-serial-fraction",
    "A profile shows that 20 percent of a job's time is serial. What is the most that 64 workers can give, and what would help more than another 64?",
    [
        "About 64 times; adding workers always helps in proportion",
        "About 12.8 times, since four-fifths of the 64 workers is 51 and a fifth of the work is lost on each, which leaves 12.8 after rounding",
        "About 4.7 times, never more than 5; shrinking the serial fifth helps more than any number of extra workers",
        "Exactly 5 times at 64 workers, and 10 times at 128",
    ],
    2,
    "Amdahl: 1 over (0.2 plus 0.8 over 64) is 4.7, and the limit as workers grow is 1 over 0.2, which is 5. Doubling the workers to 128 gives 4.85, almost nothing. Halving the serial part to a tenth raises the limit to 10 and the 64-worker figure to 8.8. With many workers, the serial fraction is the only number that matters.",
    ["amdahl"],
)

write(
    "recall/review-predict-intensity-of-elementwise.yaml",
    f'''id: review-predict-intensity-of-elementwise
type: predict_output
rev: 1
prompt: |
  The FLOPs per byte of three operations on a million float32 values (an add reads two arrays and writes one; a scale in place reads one and writes one; a dot product reads two and does a multiply and an add per element), and the ridge of a machine. What does the program print?
code: |
{block(REVIEW_INTENSITY)}expected_output: |
{block(REVIEW_INTENSITY_OUT)}explanation: |
  Elementwise work does about one operation per element however the bytes are counted: the add is 1 FLOP per 12 bytes, the in-place scale 1 per 8, the dot product 2 per 8. All three are far below the ridge of 20, so on that machine they are memory-bound and its FLOP rate never matters to them; only the bytes do.
skills: [intensity]
''',
)

mcq(
    "review-mcq-memory-bound-step",
    "An elementwise step (normalize, then activate, then scale) is memory-bound on the GPU. Which change speeds it up?",
    [
        "A GPU with twice the FLOP rate and the same memory bandwidth",
        "Running the three operations in three separate streams at the same time",
        "Switching the arithmetic from float32 to float64, so that each operation does more work for every byte it fetches",
        "Fusing the three into one pass, so the array is read and written once instead of three times",
    ],
    3,
    "Below the ridge the time is bytes over bandwidth, so the fixes are fewer bytes or more bandwidth. Three passes read and write the array three times; one fused pass does it once, a third of the traffic. More FLOP rate changes nothing a memory-bound step can feel, three streams compete for the same bandwidth, and float64 doubles the bytes. Halving the precision to float16 would help, for the same reason fusing does.",
    ["bandwidth"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-amdahl-and-a-matrix-multiply/exercise.yaml",
    f'''id: example-amdahl-and-a-matrix-multiply
stage: worked_example
rev: 1
title: "Amdahl's law and a matrix multiply"
prompt: |
  Amdahl's law for three parallel fractions; a million items that split and a million steps that don't; the FLOPs and bytes of a matrix multiply and of a vector add; a roofline of round numbers; why a batch raises the FLOPs per byte; and what a transfer across the bus costs. Press **Run**, then read how each part works.
steps:
  - label: "Amdahl's law"
    lines: "{ln('def speedup')}-{ln('| limit')}"
    note: "The serial part keeps its whole time; the parallel part is divided among the workers. At 50 percent parallel no number of workers gets past 2 times, at 90 percent past 10, at 99 past 100. The line for each fraction flattens as the workers grow: 90 percent on 64 workers is 8.8 times, and 1,000 workers add only one more."
  - label: "What splits and what doesn't"
    lines: "{ln('items = 1_000_000')}-{ln('independent items on 8 workers')}"
    note: "A million independent items on 8 workers is 125,000 each; a chain where each step needs the previous step's result is a million steps however many workers wait beside it. The parallel fraction in Amdahl's law is the share of the work that is the first kind."
  - label: "Counting a matrix multiply, and a vector add"
    lines: "{ln('def matmul_cost')}-{ln('adding two vectors of a million')}"
    note: "Each of the `m * n` outputs sums `k` products, a multiply and an add per term: `2 * m * k * n` FLOPs. The bytes are both inputs read and the output written. A 1024-cube in float32 is 2.1 billion FLOPs over 12.6 megabytes, 171 FLOPs per byte; adding two vectors of a million is 1 FLOP per 12 bytes."
  - label: "A roofline of round numbers"
    lines: "{ln('FLOP_RATE, BANDWIDTH')}-{ln('us of arithmetic')}"
    note: "A machine that does 10 TFLOP/s and moves 500 GB/s can do 20 FLOPs for every byte it fetches: its ridge. Above the ridge the arithmetic takes longer than the fetching and sets the time (the multiply: 215 microseconds against 25); below it the fetching does (the add: 24 microseconds of traffic for a tenth of a microsecond of arithmetic). The machine overlaps the two, so the time is the larger."
  - label: "Why batches help"
    lines: "{ln('k, n = 1024, 1024')}-{ln('the weights read once per batch')}"
    note: "A layer's weights are read once per batch, so the FLOPs per byte of `(batch, 1024) @ (1024, 1024)` rise with the batch: 0.5 at a batch of 1, 3.9 at 8, 28 at 64, 128 at 512. Below the ridge of 20 the GPU waits on memory; above it, it computes. One example at a time is on the wrong side."
  - label: "Crossing the bus"
    lines: "{ln('BUS, LATENCY')}-{ln('moving a 1 GB dataset')}"
    note: "The bus between CPU and GPU memory moves tens of gigabytes per second and charges a fixed latency per transfer. A gigabyte in one piece is 40 milliseconds; the same gigabyte as a million small pieces is 10 seconds, nearly all of it the per-transfer cost. Data moves once and stays."
''',
)
write("exercises/example-amdahl-and-a-matrix-multiply/solution.py", EXAMPLE)
write(
    "exercises/example-amdahl-and-a-matrix-multiply/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints Amdahl's table, the split, the two counts, the roofline, the batch sizes and the transfer."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-arithmetic-intensity/exercise.yaml",
    f'''id: fill-arithmetic-intensity
stage: fill_in
rev: 1
title: "FLOPs per byte"
prompt: |
  `arithmetic_intensity(m, k, n, itemsize)` should return the FLOPs per byte of `(m, k) @ (k, n)`: two operations per term of each of the `m * n` outputs (a multiply and an add, `k` terms each), over the bytes of both inputs and the output. Replace each `...` so the program prints the intensity of a 1024-cube in float32, then of a batch of 1 and of 64 against a `(1024, 1024)` weight matrix:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "Each output is a sum of `k` products: `k` multiplies and `k` adds, so 2 operations per term."
  - "The three arrays are `(m, k)`, `(k, n)` and `(m, n)`; their element counts are `m * k`, `k * n` and `m * n`."
skills: [intensity]
''',
)
write("exercises/fill-arithmetic-intensity/starter.py", FILL_STARTER)
write("exercises/fill-arithmetic-intensity/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-arithmetic-intensity/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the three intensities."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_more_shapes():
    """A (2, 3) @ (3, 4) in float64 is 48 FLOPs over 208 bytes, and float16 doubles the intensity of a 256-cube."""
    arithmetic_intensity = function("arithmetic_intensity")
    assert abs(arithmetic_intensity(2, 3, 4, 8) - 48 / 208) < 1e-12
    assert abs(arithmetic_intensity(256, 256, 256, 2) - 2 * arithmetic_intensity(256, 256, 256, 4)) < 1e-9
''',
)
write("exercises/fill-arithmetic-intensity/wrong/half-the-flops.py", FILL_WRONG)
write(
    "exercises/fill-arithmetic-intensity/wrong/typed-in.py",
    "def arithmetic_intensity(m, k, n, itemsize):\n    return 170.7\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-speedup-and-roofline/exercise.yaml",
    f'''id: write-speedup-and-roofline
stage: write
rev: 1
title: "Amdahl and the roofline"
prompt: |
  Write `speedup(parallel_fraction, workers)`, Amdahl's law (1 over the serial fraction plus the parallel fraction divided by the workers), and `roofline_seconds(flops, bytes_moved, flop_rate, bandwidth)`, the time a machine needs for the arithmetic or for the bytes, whichever is longer, since it overlaps the two. Then print:

  ```python
  print(round(speedup(0.9, 8), 2), round(speedup(0.9, 10**6), 2))
  print(round(roofline_seconds(2 * 1024**3, 3 * 1024**2 * 4, 10e12, 500e9) * 1e6, 1))
  print(round(roofline_seconds(1_000_000, 12_000_000, 10e12, 500e9) * 1e6, 1))
  ```

  ```
{block(WRITE_OUT)}  ```

  The first roofline line is a 1024-cube matrix multiply in float32 on a 10 TFLOP/s, 500 GB/s machine, in microseconds; the second is a vector add of a million float32.
hints:
  - "The serial fraction is `1 - parallel_fraction`; the speed-up is 1 over the time that remains."
  - "The two times are `flops / flop_rate` and `bytes_moved / bandwidth`; `max` picks the longer."
skills: [amdahl, intensity]
''',
)
write("exercises/write-speedup-and-roofline/starter.py", "")
write("exercises/write-speedup-and-roofline/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-speedup-and-roofline/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the speed-ups and the two roofline times."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_limits():
    """Fully parallel work speeds up by the worker count, fully serial work not at all, and the roofline picks the longer time either way round."""
    speedup = function("speedup")
    roofline_seconds = function("roofline_seconds")
    assert abs(speedup(1.0, 16) - 16) < 1e-9 and abs(speedup(0.0, 16) - 1) < 1e-9
    assert abs(roofline_seconds(1e9, 1e6, 1e12, 1e9) - 1e-3) < 1e-12
    assert abs(roofline_seconds(1e6, 1e9, 1e12, 1e9) - 1.0) < 1e-12
''',
)
write("exercises/write-speedup-and-roofline/wrong/summed.py", WRITE_SUMMED)
write("exercises/write-speedup-and-roofline/wrong/inverted.py", WRITE_INVERTED)
write(
    "exercises/write-speedup-and-roofline/wrong/typed-in.py",
    "def speedup(parallel_fraction, workers):\n    return 4.71\n\n\ndef roofline_seconds(flops, bytes_moved, flop_rate, bandwidth):\n    return 0.0002147\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-a-parallel-cost-toolkit/exercise.yaml",
    f'''id: build-a-parallel-cost-toolkit
stage: build
rev: 1
title: "A parallel cost toolkit"
prompt: |
  Starting from a blank editor, write five functions:

  - `amdahl(parallel_fraction, workers)`: the speed-up Amdahl's law allows.
  - `matmul_cost(m, k, n, itemsize)`: the tuple `(FLOPs, bytes)` of `(m, k) @ (k, n)`: a multiply and an add per term of each output; both inputs read and the output written, `itemsize` bytes per element.
  - `intensity(flops, bytes_moved)`: FLOPs per byte.
  - `roofline_seconds(flops, bytes_moved, flop_rate, bandwidth)`: the longer of the arithmetic time and the memory time.
  - `transfer_seconds(total_bytes, pieces, bandwidth, latency)`: the time to move `total_bytes` across a bus in that many pieces: the bytes at the bandwidth, plus a fixed latency per piece.

  Then print:

  ```python
  print(round(amdahl(0.9, 8), 2), round(amdahl(0.9, 10**9), 2), round(amdahl(0.99, 64), 1))
  print(matmul_cost(1024, 1024, 1024, 4), round(intensity(*matmul_cost(1024, 1024, 1024, 4)), 1))
  print(round(intensity(*matmul_cost(1, 1024, 1024, 4)), 2), round(intensity(*matmul_cost(512, 1024, 1024, 4)), 1))
  print(round(roofline_seconds(*matmul_cost(1024, 1024, 1024, 4), 10e12, 500e9) * 1e6, 1), round(roofline_seconds(1_000_000, 12_000_000, 10e12, 500e9) * 1e6, 1))
  print(round(transfer_seconds(10**9, 1, 25e9, 10e-6), 3), round(transfer_seconds(10**9, 10**6, 25e9, 10e-6), 2))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks try the limits of Amdahl's law, compare the matrix multiply counts with a hand count on small shapes, test the roofline on both sides of the ridge, and move the same bytes in one piece and in many.
skills: [amdahl, intensity, bandwidth]
''',
)
write("exercises/build-a-parallel-cost-toolkit/starter.py", "")
write("exercises/build-a-parallel-cost-toolkit/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-a-parallel-cost-toolkit/test_exercise.py",
    f'''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the five lines."""
    assert run() == {BUILD_OUT!r}


def test_amdahl_limits():
    """Fully parallel work speeds up by the worker count, fully serial not at all, and a fifth serial never passes 5."""
    amdahl = function("amdahl")
    assert abs(amdahl(1.0, 32) - 32) < 1e-9 and abs(amdahl(0.0, 32) - 1) < 1e-9
    assert amdahl(0.8, 64) < 5 and abs(amdahl(0.8, 10**12) - 5) < 1e-6


def test_matmul_counts():
    """(2, 3) @ (3, 4) in float64 is 48 FLOPs and 208 bytes; (5, 7) @ (7, 2) in float16 is 140 FLOPs and 118 bytes."""
    matmul_cost = function("matmul_cost")
    assert tuple(matmul_cost(2, 3, 4, 8)) == (48, 208)
    assert tuple(matmul_cost(5, 7, 2, 2)) == (140, 118)


def test_roofline_both_sides():
    """Above the ridge the arithmetic time wins, below it the memory time, and intensity is FLOPs over bytes."""
    intensity = function("intensity")
    roofline_seconds = function("roofline_seconds")
    assert abs(intensity(48, 208) - 48 / 208) < 1e-12
    assert abs(roofline_seconds(1e9, 1e6, 1e12, 1e9) - 1e-3) < 1e-12
    assert abs(roofline_seconds(1e6, 1e9, 1e12, 1e9) - 1.0) < 1e-12


def test_transfer():
    """A gigabyte in one piece at 25 GB/s is 40 ms plus one latency; in a thousand pieces it costs a thousand latencies."""
    transfer_seconds = function("transfer_seconds")
    assert abs(transfer_seconds(10**9, 1, 25e9, 1e-5) - 0.04001) < 1e-9
    assert abs(transfer_seconds(10**9, 1000, 25e9, 1e-5) - 0.05) < 1e-9
''',
)
write("exercises/build-a-parallel-cost-toolkit/wrong/inverted-amdahl.py", BUILD_INVERTED)
write("exercises/build-a-parallel-cost-toolkit/wrong/half-the-flops.py", BUILD_HALF_FLOPS)
write("exercises/build-a-parallel-cost-toolkit/wrong/summed-roofline.py", BUILD_SUMMED)
write("exercises/build-a-parallel-cost-toolkit/wrong/no-latency.py", BUILD_NO_LATENCY)
write(
    "exercises/build-a-parallel-cost-toolkit/wrong/typed-in.py",
    "def amdahl(parallel_fraction, workers):\n    return 4.71\n\n\ndef matmul_cost(m, k, n, itemsize):\n    return (2147483648, 12582912)\n\n\ndef intensity(flops, bytes_moved):\n    return 170.7\n\n\ndef roofline_seconds(flops, bytes_moved, flop_rate, bandwidth):\n    return 0.0002147\n\n\ndef transfer_seconds(total_bytes, pieces, bandwidth, latency):\n    return 0.04\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-speed-up-and-a-count/exercise.yaml",
    f'''id: debug-a-speed-up-and-a-count
stage: debug
rev: 1
title: "A speed-up and a count"
prompt: |
  `amdahl` should give the speed-up of 90 percent parallel work on 8 workers, and `matmul_cost` the FLOPs and bytes of a 1024-cube in float32. The program should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the speed-up comes out `1.10x`, because the fractions are the wrong way round: it is the **parallel** part that gets divided among the workers and the serial part that stays whole. Fix that, and the matrix multiply counts `1,073,741,824` FLOPs, half the right number: each term of an output is a multiply **and** an add, so the count is `2 * m * k * n`, and the FLOPs per byte are 170.7, not 85.3.
skills: [amdahl, intensity]
''',
)
write("exercises/debug-a-speed-up-and-a-count/starter.py", DEBUG_STARTER)
write("exercises/debug-a-speed-up-and-a-count/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-speed-up-and-a-count/test_exercise.py",
    f'''from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the right speed-up and the right counts."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_other_values():
    """Fully parallel work on 4 workers is 4 times; (2, 3) @ (3, 4) in float64 is 48 FLOPs and 208 bytes."""
    amdahl = function("amdahl")
    matmul_cost = function("matmul_cost")
    assert abs(amdahl(1.0, 4) - 4) < 1e-9 and abs(amdahl(0.5, 10**9) - 2) < 1e-6
    assert tuple(matmul_cost(2, 3, 4, 8)) == (48, 208)
''',
)
write("exercises/debug-a-speed-up-and-a-count/wrong/still-swapped.py", DEBUG_STILL_SWAPPED)
write("exercises/debug-a-speed-up-and-a-count/wrong/still-half.py", DEBUG_STILL_HALF)
write(
    "exercises/debug-a-speed-up-and-a-count/wrong/typed-in.py",
    "def amdahl(parallel_fraction, workers):\n    return 4.71\n\n\ndef matmul_cost(m, k, n, itemsize):\n    return 2147483648, 12582912\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-amdahl/exercise.yaml",
    f'''id: review-amdahl
stage: review_code
rev: 1
title: "Amdahl's law, from memory"
prompt: |
  Write `speedup(parallel_fraction, workers)`, Amdahl's law, and print the speed-up of 80 percent parallel work on 4 workers, on 64, and on a billion, each rounded to 2 places:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [amdahl]
''',
)
write("exercises/review-amdahl/starter.py", "")
write("exercises/review-amdahl/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-amdahl/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the three speed-ups."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_limits():
    """Fully parallel work speeds up by the worker count; a tenth serial never passes 10."""
    speedup = function("speedup")
    assert abs(speedup(1.0, 7) - 7) < 1e-9 and speedup(0.9, 10**6) < 10 and speedup(0.9, 10**6) > 9.99
''',
)
write("exercises/review-amdahl/wrong/inverted.py", REVIEW_CODE_WRONG)
write(
    "exercises/review-amdahl/wrong/typed-in.py",
    "def speedup(parallel_fraction, workers):\n    return 2.5\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.hw.parallelism-and-gpus written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
