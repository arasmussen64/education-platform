"""Outlines Module 7 of the ML Foundations track, how computers and GPUs work:
planned topic.yaml files, the module in the track file, and the spec's prose
bullet turned into a table. Run from the repository root under uv. Never
overwrites a topic that isn't a planned outline."""

import pathlib

import yaml

ROOT = pathlib.Path(".")
TOPICS = ROOT / "content" / "topics"
TRACK_PATH = ROOT / "content" / "tracks" / "ml-foundations.yaml"
SPEC = ROOT / "docs" / "specs" / "ml-foundations.md"

MODULE = {
    "id": "ml.m7",
    "title": "How computers and GPUs work",
    "topics": [
        "ml.hw.bits-and-integers",
        "ml.hw.floating-point",
        "ml.hw.memory-and-caches",
        "ml.hw.vectorization",
        "ml.hw.parallelism-and-gpus",
        "ml.hw.cost-of-a-model",
        "ml.hw.profiling",
    ],
    "checkpoint": "ml.m7.checkpoint",
}

# id: (kind, title, summary, prerequisites, minutes, objectives, "you'll be able to" for the spec)
OUTLINES = {
    "ml.hw.bits-and-integers": (
        "topic", "Bits, bytes and integers",
        "How a computer stores a whole number: binary and hexadecimal, bytes, fixed-width integers that wrap around, Python's integers that don't, and the bit operations that masks and flags are made of.",
        ["ml.m6.checkpoint"], 45,
        ["Convert between binary, decimal and hexadecimal, and read a byte.",
         "Explain what a fixed-width integer is, why an int8 wraps from 127 to -128, and why a Python int doesn't.",
         "Say how many bytes a NumPy array of a given dtype and shape takes, and choose a dtype for a column of counts.",
         "Use and, or, shift and masks to pack and read flags."],
        "convert between binary, decimal and hexadecimal; explain why an int8 wraps from 127 to -128 and a Python int doesn't; size a NumPy array from its dtype and shape and choose a dtype for a column; pack and read flags with bit operations"),
    "ml.hw.floating-point": (
        "topic", "Floating point",
        "How a computer stores a fraction: sign, exponent and mantissa; why 0.1 + 0.2 isn't 0.3; float32 against float64; machine epsilon, rounding that accumulates, overflow to infinity, NaN, and the log-sum-exp trick that keeps a loss finite.",
        ["ml.hw.bits-and-integers"], 55,
        ["Explain how a float stores a number as sign, exponent and mantissa, and why most decimals are stored approximately.",
         "Compare two floats safely with a tolerance, and say what machine epsilon is for float32 and float64.",
         "Show rounding error accumulating in a long sum, and reduce it with pairwise or compensated summation.",
         "Say where infinity and NaN come from, and keep a softmax or a log-likelihood finite with log-sum-exp."],
        "explain sign, exponent and mantissa and why 0.1 is stored approximately; compare floats with a tolerance and state machine epsilon for float32 and float64; show rounding accumulating in a sum and reduce it; say where inf and NaN come from and use log-sum-exp"),
    "ml.hw.memory-and-caches": (
        "topic", "Memory, caches and locality",
        "The memory hierarchy from registers to disk, why touching nearby bytes is cheap and far-apart bytes dear, how NumPy lays an array out in memory (row-major order, strides, views against copies), and why looping over the wrong axis is slow.",
        ["ml.hw.bits-and-integers"], 50,
        ["Name the levels of the memory hierarchy and the rough cost of each, and say what a cache line is.",
         "Explain how NumPy stores a 2-D array in memory, read strides, and tell a view from a copy.",
         "Predict which loop order over a matrix touches memory in sequence, and show the difference by counting cache lines.",
         "Say why a model's weights and activations are measured in bytes moved, not only in operations."],
        "name the memory hierarchy's levels and rough costs and say what a cache line is; read a NumPy array's strides and tell a view from a copy; predict which loop order is cache-friendly and show it by counting cache lines; say why bytes moved matter as much as operations"),
    "ml.hw.vectorization": (
        "topic", "Why vectorized code is fast",
        "What the interpreter does for every Python operation and what a NumPy operation skips, SIMD, broadcasting as a loop you don't write, the doubling test on a loop against its vectorized form, and when a loop can't be vectorized.",
        ["ml.hw.memory-and-caches", "ml.dsa.complexity"], 50,
        ["Explain what a Python loop pays per element that a NumPy operation doesn't, and what SIMD adds.",
         "Rewrite a loop over an array as array operations with broadcasting, and check that the two agree.",
         "Measure the loop and the vectorized form with the doubling test, and read the constant against the order.",
         "Recognize a loop that can't be vectorized because each step depends on the last, and say what to do instead."],
        "explain what a Python loop pays per element and what SIMD adds; vectorize a loop with broadcasting and check it agrees; measure both forms with the doubling test; recognize a sequential dependence and say what to do instead"),
    "ml.hw.parallelism-and-gpus": (
        "topic", "Parallelism and what a GPU is good at",
        "Cores and threads, work that splits and work that doesn't, Amdahl's law computed, a GPU as thousands of simple cores doing the same operation on different data, memory bandwidth as the usual limit, and why a matrix multiply is the operation GPUs were built for.",
        ["ml.hw.vectorization"], 50,
        ["Tell data parallelism from a sequential dependence, and compute the speed-up Amdahl's law allows.",
         "Explain what a GPU is: many simple cores running the same instruction on different data, with its own memory.",
         "Count the operations and the bytes of a matrix multiply, and say why its arithmetic intensity suits a GPU.",
         "Say what memory bandwidth limits, why batches help, and what moving data between CPU and GPU costs."],
        "tell data parallelism from a sequential dependence and apply Amdahl's law; explain what a GPU is; count the operations and bytes of a matrix multiply and say why it suits a GPU; say what bandwidth limits, why batches help and what the CPU-GPU transfer costs"),
    "ml.hw.cost-of-a-model": (
        "topic", "Counting a model's cost",
        "Parameters, FLOPs and bytes: counting a network's weights, the operations of a forward and backward pass, memory for weights and activations at float32 and float16, and an estimate of time from a GPU's throughput.",
        ["ml.hw.parallelism-and-gpus", "ml.hw.floating-point"], 50,
        ["Count the parameters of a network from its layer sizes.",
         "Count the FLOPs of a forward pass and estimate the backward pass, for one example and for a batch.",
         "Compute the memory for weights and activations at float32 and float16, and say what mixed precision trades.",
         "Estimate training time from FLOPs and a GPU's throughput, and say why the estimate is optimistic."],
        "count a network's parameters from its layer sizes; count the FLOPs of a forward pass and estimate the backward; compute memory for weights and activations at float32 and float16; estimate time from FLOPs and throughput and say why it is optimistic"),
    "ml.hw.profiling": (
        "topic", "Reading a profiler",
        "Finding where a program spends its time and memory: cProfile and pstats for calls and time, tracemalloc for allocations, the doubling test for growth, and the discipline of measuring before optimizing.",
        ["ml.hw.vectorization"], 50,
        ["Profile a program with cProfile, read the call counts and cumulative times in pstats, and find the hot spot.",
         "Measure peak memory and the biggest allocations with tracemalloc.",
         "Decide from a profile what to change first, change it, and show the profile after.",
         "Say why measuring beats guessing, and what a profiler's overhead does to small numbers."],
        "profile with cProfile and read pstats to find the hot spot; measure memory with tracemalloc; choose what to change first from a profile and show the result; say why measuring beats guessing"),
    "ml.m7.checkpoint": (
        "checkpoint", "Checkpoint 7: make it fast",
        "A slow, numerically shaky feature pipeline: profile it, vectorize the hot loop, fix the integer overflow and the float drift, keep a softmax finite, and estimate the cost of the model it feeds.",
        ["ml.hw.floating-point", "ml.hw.cost-of-a-model", "ml.hw.profiling"], 120,
        ["Profile a slow pipeline, find its hot loop and vectorize it, and show the gain with the doubling test and the profile.",
         "Find and fix three numeric bugs: an int8 column that wraps, a float32 sum that drifts, and a softmax that overflows to NaN.",
         "Estimate the parameters, FLOPs and memory of the model the pipeline feeds, and explain floating point and why vectorized code is fast."],
        None),
}

MARKER = (
    "# A planned outline for the Machine Learning Foundations track\n"
    "# (docs/specs/ml-foundations.md). It becomes real content when written.\n"
)


class Dumper(yaml.SafeDumper):
    pass


def str_presenter(dumper, data):
    style = '"' if any(ch in data for ch in ":#'\"") else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


Dumper.add_representer(str, str_presenter)


def dump(data) -> str:
    return yaml.dump(data, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=1000)


# --- the track file ------------------------------------------------------------------------

track = yaml.safe_load(TRACK_PATH.read_bytes().decode("utf-8"))
if not any(module["id"] == "ml.m7" for module in track["modules"]):
    track["modules"].append(MODULE)
    TRACK_PATH.write_bytes(dump(track).encode("utf-8"))
    print("wrote", TRACK_PATH)
else:
    print("track already has ml.m7")

# --- the planned topics ------------------------------------------------------------------------

for topic_id, (kind, title, summary, prereqs, minutes, objectives, _) in OUTLINES.items():
    folder = TOPICS / topic_id
    path = folder / "topic.yaml"
    if path.exists() and "status: planned" not in path.read_bytes().decode("utf-8"):
        print("kept (being written)", path)
        continue
    folder.mkdir(parents=True, exist_ok=True)
    outline = {
        "id": topic_id,
        "kind": kind,
        "status": "planned",
        "title": title,
        "summary": summary,
        "prerequisites": prereqs,
        "estimated_minutes": minutes,
        "rev": 1,
        "objectives": objectives,
    }
    path.write_bytes((MARKER + dump(outline)).encode("utf-8"))
    print("wrote", path)

# --- the spec: the prose bullet becomes a table --------------------------------------------------

spec = SPEC.read_bytes().decode("utf-8")
if "## Module 7: How computers and GPUs work" not in spec:
    rows = []
    for number, topic_id in enumerate(MODULE["topics"], start=43):
        kind, title, summary, prereqs, minutes, objectives, able = OUTLINES[topic_id]
        needs = ", ".join(f"`{p}`" for p in prereqs)
        rows.append(f"| {number} | {title} | `{topic_id}` | {needs} | {able} |")
    section = (
        "## Module 7: How computers and GPUs work\n\n"
        "Module 6 counted steps; this module asks what a step costs and why. Bits, bytes and the integers that wrap; floating point and the rounding every loss carries; the memory hierarchy and why nearby bytes are cheap; why vectorized code is fast and when a loop can't be; parallelism, Amdahl's law and what a GPU is good at; counting a model's parameters, FLOPs and bytes; and reading a profiler. Every topic is proven in code where the browser can run it: the checks count operations, bytes and calls, and timings stay in prose, because Pyodide is 32-bit and its clock and object sizes differ from CPython's.\n\n"
        "| # | Topic | ID | Needs | You'll be able to… |\n"
        "| --- | --- | --- | --- | --- |\n"
        + "\n".join(rows)
        + "\n\n"
        "**Checkpoint 7: make it fast** (`ml.m7.checkpoint`). Profile a slow, numerically shaky feature pipeline, find its hot loop and vectorize it, showing the gain with the doubling test and the profile; fix three numeric bugs (an int8 column that wraps, a float32 sum that drifts, a softmax that overflows to NaN); estimate the parameters, FLOPs and memory of the model the pipeline feeds; and explain floating point and why vectorized code is fast. The way through for a stuck learner, as in the earlier checkpoints: a solved sibling, steps, fresh versions.\n\n"
    )
    old_bullet = "- **7. How computers and GPUs work:** memory and caches; why vectorized code is fast; floating point; what a GPU is good at; reading a profiler.\n"
    assert old_bullet in spec, "the Module 7 prose bullet has changed"
    spec = spec.replace(old_bullet, "")
    old_sentence = "as Modules 3 to 6 had before they were written (all four on 2026-11-10)."
    assert old_sentence in spec, "the later-modules sentence has changed"
    spec = spec.replace(old_sentence, "as Modules 3 to 6 had before they were written (all four on 2026-11-10) and Module 7 has (outlined 2026-11-10).")
    assert spec.count("## Later modules") == 1
    spec = spec.replace("## Later modules", section + "## Later modules")
    SPEC.write_bytes(spec.encode("utf-8"))
    print("wrote", SPEC)
else:
    print("spec already has Module 7")
