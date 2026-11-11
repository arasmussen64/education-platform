"""Writes the topic ml.hw.memory-and-caches (Module 7's third topic). Run from
the repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Strides are printed only for arrays with a named dtype, cache behaviour is
simulated rather than timed, and nothing depends on the platform's word size.
Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.hw.memory-and-caches")


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


SIMULATOR = '''def misses(shape, order, lines_in_cache, floats_per_line=8):
    """Cache misses when a float64 matrix is walked in row or column order through a small least-recently-used cache."""
    rows, cols = shape
    if order == "rows":
        visits = ((r, c) for r in range(rows) for c in range(cols))
    else:
        visits = ((r, c) for c in range(cols) for r in range(rows))
    cache = OrderedDict()
    count = 0
    for r, c in visits:
        line = (r, c // floats_per_line)
        if line in cache:
            cache.move_to_end(line)
        else:
            count += 1
            cache[line] = True
            if len(cache) > lines_in_cache:
                cache.popitem(last=False)
    return count
'''

# --- the worked example ----------------------------------------------------------------------

EXAMPLE = '''from collections import OrderedDict

import numpy as np

a = np.arange(12, dtype=np.float64).reshape(3, 4)
print("strides:", a.strides, "| transposed:", a.T.strides, "| contiguous:", a.flags["C_CONTIGUOUS"], a.T.flags["C_CONTIGUOUS"])
print("a[1, 2] sits", 1 * a.strides[0] + 2 * a.strides[1], "bytes from the start; row 1 occupies bytes", a.strides[0], "to", 2 * a.strides[0] - 1)

every_other_column = a[:, ::2]
big_ones = a[a > 5]
print("shares memory: slice", np.shares_memory(a, every_other_column), "| mask", np.shares_memory(a, big_ones), "| slice strides", every_other_column.strides)
every_other_column[0, 0] = 100
print("after writing 100 through the view, a[0, 0] is", a[0, 0])


''' + SIMULATOR + '''

for order in ("rows", "columns"):
    print(f"256 x 256 floats walked by {order}, 64 lines of cache: {misses((256, 256), order, 64):,} misses")

grid = np.zeros((1000, 1000), dtype=np.float64)
print("a 1000 x 1000 float64 grid is", f"{grid.nbytes:,}", "bytes")
doubled = grid + 1
grid += 1
print("grid + 1 made a new block:", not np.shares_memory(grid, doubled), "| grid += 1 wrote in place:", grid[0, 0])
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert EX[0] == "strides: (32, 8) | transposed: (8, 32) | contiguous: True False", EX[0]
assert EX[1] == "a[1, 2] sits 48 bytes from the start; row 1 occupies bytes 32 to 63", EX[1]
assert EX[2] == "shares memory: slice True | mask False | slice strides (32, 16)", EX[2]
assert EX[3] == "after writing 100 through the view, a[0, 0] is 100.0", EX[3]
assert EX[4] == "256 x 256 floats walked by rows, 64 lines of cache: 8,192 misses", EX[4]
assert EX[5] == "256 x 256 floats walked by columns, 64 lines of cache: 65,536 misses", EX[5]
assert EX[6] == "a 1000 x 1000 float64 grid is 8,000,000 bytes", EX[6]
assert EX[7] == "grid + 1 made a new block: True | grid += 1 wrote in place: 1.0", EX[7]
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_STRIDES = '''import numpy as np

a = np.zeros((4, 5), dtype=np.float32)
print(a.strides, a.T.strides)
print(a[::2].strides, a[:, 1:3].strides)
print(np.zeros((2, 3, 4), dtype=np.int16).strides)
'''
PREDICT_STRIDES_OUT = out(PREDICT_STRIDES)
assert PREDICT_STRIDES_OUT == "(20, 4) (4, 20)\n(40, 4) (20, 4)\n(24, 8, 2)\n", PREDICT_STRIDES_OUT

PREDICT_VIEWS = '''import numpy as np

a = np.arange(6, dtype=np.int32).reshape(2, 3)
rows = a[1:]
flipped = a.T
chosen = a[a % 2 == 0]
fresh = a.copy()
print(np.shares_memory(a, rows), np.shares_memory(a, flipped), np.shares_memory(a, chosen), np.shares_memory(a, fresh))
rows[0, 0] = 99
chosen[0] = 77
print(a[1, 0], a[0, 0])
'''
PREDICT_VIEWS_OUT = out(PREDICT_VIEWS)
assert PREDICT_VIEWS_OUT == "True True False False\n99 0\n", PREDICT_VIEWS_OUT

REVIEW_MISSES = "from collections import OrderedDict\n\n\n" + SIMULATOR + '''

print(misses((16, 16), "rows", 2), misses((16, 16), "columns", 2), misses((16, 16), "columns", 16))
'''
REVIEW_MISSES_OUT = out(REVIEW_MISSES)
assert REVIEW_MISSES_OUT == "32 256 32\n", REVIEW_MISSES_OUT

PARSONS_LINES = [
    "import numpy as np",
    "a = np.zeros((3, 4), dtype=np.float64)",
    "top_row = a[0]",
    "top_row[:] = 7",
    "print(a[0, 0], np.shares_memory(a, top_row))",
]
assert out("\n".join(PARSONS_LINES) + "\n") == "7.0 True\n"
assert out("\n".join(PARSONS_LINES).replace("top_row = a[0]", "top_row = a[0].copy()") + "\n") == "0.0 False\n"

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''def c_strides(shape, itemsize):
    """The byte strides NumPy uses for a C-order (row-major) array: the last axis steps one item, each earlier axis steps a whole block."""
    strides = []
    step = itemsize
    for size in reversed(shape):
        strides.append(step)
        step *= size
    return tuple(reversed(strides))


print(c_strides((3, 4), 8), c_strides((4, 5), 4), c_strides((2, 3, 4), 2))
'''
FILL_STARTER = FILL_SOLUTION.replace("    step = itemsize\n", "    step = ...\n").replace("        step *= size\n", "        step *= ...\n")
FILL_WRONG = FILL_SOLUTION.replace("    for size in reversed(shape):", "    for size in shape:").replace("    return tuple(reversed(strides))", "    return tuple(strides)")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "(32, 8) (20, 4) (24, 8, 2)\n", FILL_OUT
assert out(FILL_WRONG) != FILL_OUT

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = "from collections import OrderedDict\n\n\n" + SIMULATOR + '''

for order in ("rows", "columns"):
    print(order, misses((128, 128), order, 32))
print(misses((8, 8), "columns", 8))
'''
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "rows 2048\ncolumns 16384\n8\n", WRITE_OUT
WRITE_WRONG = WRITE_SOLUTION.replace("            if len(cache) > lines_in_cache:\n                cache.popitem(last=False)\n", "")
WRITE_LINE_PER_ELEMENT = WRITE_SOLUTION.replace("        line = (r, c // floats_per_line)", "        line = (r, c)")
assert WRITE_WRONG != WRITE_SOLUTION and out(WRITE_WRONG) != WRITE_OUT and out(WRITE_LINE_PER_ELEMENT) != WRITE_OUT

# --- the build ----------------------------------------------------------------------------------

BUILD_SOLUTION = '''from collections import OrderedDict

import numpy as np


def c_strides(shape, itemsize):
    """The byte strides of a C-order array of that shape and item size."""
    strides = []
    step = itemsize
    for size in reversed(shape):
        strides.append(step)
        step *= size
    return tuple(reversed(strides))


def byte_offset(shape, itemsize, index):
    """How many bytes from the start of a C-order array the element at index sits."""
    return sum(i * s for i, s in zip(index, c_strides(shape, itemsize)))


''' + SIMULATOR + '''

def traffic(shape, dtype, reads, writes):
    """Bytes moved by an operation that reads the whole array `reads` times and writes it `writes` times."""
    elements = 1
    for size in shape:
        elements *= size
    return elements * np.dtype(dtype).itemsize * (reads + writes)


print(c_strides((3, 4), 8), byte_offset((3, 4), 8, (1, 2)), byte_offset((2, 3, 4), 2, (1, 2, 3)))
print(misses((256, 256), "rows", 64), misses((256, 256), "columns", 64))
print(traffic((1000, 1000), "float64", 1, 0), traffic((1000, 1000), "float64", 1, 1), traffic((1000, 1000), "float32", 1, 1))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == "(32, 8) 48 46\n8192 65536\n8000000 16000000 8000000\n", BUILD_OUT
BUILD_FORTRAN_STRIDES = BUILD_SOLUTION.replace("    for size in reversed(shape):\n        strides.append(step)\n        step *= size\n    return tuple(reversed(strides))", "    for size in shape:\n        strides.append(step)\n        step *= size\n    return tuple(strides)")
BUILD_NO_EVICTION = BUILD_SOLUTION.replace("            if len(cache) > lines_in_cache:\n                cache.popitem(last=False)\n", "")
BUILD_TRAFFIC_ELEMENTS = BUILD_SOLUTION.replace("    return elements * np.dtype(dtype).itemsize * (reads + writes)", "    return elements * (reads + writes)")
for wrong in (BUILD_FORTRAN_STRIDES, BUILD_NO_EVICTION, BUILD_TRAFFIC_ELEMENTS):
    assert wrong != BUILD_SOLUTION and out(wrong) != BUILD_OUT

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''import numpy as np


def byte_offset(shape, itemsize, index):
    """Bytes from the start of a C-order array to the element at index: each earlier axis steps a whole block of later axes."""
    row, col = index
    rows, cols = shape
    return (row * cols + col) * itemsize


def clear_top_row(a):
    """Set the first row of a 2-D array to zero, in place."""
    top = a[0]
    top[:] = 0


a = np.arange(12, dtype=np.float64).reshape(3, 4)
print(byte_offset(a.shape, a.itemsize, (1, 2)), "==", 1 * a.strides[0] + 2 * a.strides[1])
clear_top_row(a)
print(a[0], a[1, 0])
'''
BUG_WRONG_AXIS = ("    return (row * cols + col) * itemsize", "    return (row * rows + col) * itemsize")
BUG_COPY = ("    top = a[0]\n    top[:] = 0", "    top = a[0].copy()\n    top[:] = 0")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_WRONG_AXIS).replace(*BUG_COPY)
DEBUG_STILL_AXIS = DEBUG_SOLUTION.replace(*BUG_WRONG_AXIS)
DEBUG_STILL_COPY = DEBUG_SOLUTION.replace(*BUG_COPY)
DEBUG_OUT = out(DEBUG_SOLUTION)
STARTER_OUT = out(DEBUG_STARTER)
print("debug:\n" + DEBUG_OUT + "starter:\n" + STARTER_OUT)
assert DEBUG_OUT == "48 == 48\n[0. 0. 0. 0.] 4.0\n", DEBUG_OUT
assert STARTER_OUT == "40 == 48\n[0. 1. 2. 3.] 4.0\n", STARTER_OUT
assert out(DEBUG_STILL_AXIS) != DEBUG_OUT and out(DEBUG_STILL_COPY) != DEBUG_OUT

REVIEW_CODE_SOLUTION = FILL_SOLUTION
REVIEW_CODE_OUT = FILL_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.hw.memory-and-caches
kind: topic
status: ready
title: "Memory, caches and locality"
summary: "The memory hierarchy from registers to disk, why touching nearby bytes is cheap and far-apart bytes dear, how NumPy lays an array out in memory (row-major order, strides, views against copies), and why looping over the wrong axis is slow."
prerequisites: [ml.hw.bits-and-integers]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Name the levels of the memory hierarchy and the rough cost of each, and say what a cache line is."
  - "Explain how NumPy stores a 2-D array in memory, read strides, and tell a view from a copy."
  - "Predict which loop order over a matrix touches memory in sequence, and show the difference by counting cache lines."
  - "Say why a model's weights and activations are measured in bytes moved, not only in operations."
# Linked, never copied or embedded: NumPy's documentation is under the NumPy
# licence (BSD-3-Clause); Wikipedia is CC BY-SA 4.0.
resources:
  - title: "NumPy user guide: Copies and views (views, the base, indexing that copies, and how to tell them apart)"
    url: https://numpy.org/doc/stable/user/basics.copies.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
  - title: "NumPy reference: the ndarray, section Internal memory layout of an ndarray (one block of bytes, strides, C and Fortran order)"
    url: https://numpy.org/doc/stable/reference/arrays.ndarray.html#internal-memory-layout-of-an-ndarray
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
  - title: "Wikipedia: CPU cache (the Overview, and the sections on cache entries and cache misses)"
    url: https://en.wikipedia.org/wiki/CPU_cache
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
practice:
  - example-rows-columns-and-cache-lines
  - mcq-what-a-cache-line-is
  - mcq-the-latency-ladder
  - predict-strides
  - predict-view-or-copy
  - parsons-write-through-a-view
  - mcq-which-loop-order
  - mcq-bytes-moved
  - fill-strides-by-hand
  - write-a-cache-simulator
prove:
  build: build-a-layout-toolkit
  debug: debug-an-offset-and-a-copy
  explain:
    prompt: |
      A teammate's feature code sums a big matrix column by column and is eight times slower than the same sum row by row; another "fixed" an array by writing into a slice of it and found the original unchanged, then found it changed the next time; a third asks why doubling a model's batch size made a memory-bound step take twice as long, so the examples per second didn't improve. In your own words: the levels of the memory hierarchy and roughly what each costs, and what a cache line is; how NumPy stores an array in memory, what strides are, and what makes an indexing operation a view or a copy; why the loop order mattered and how you would show it; and why bytes moved, not only operations, decide how fast a step runs.
    rubric:
      - id: hierarchy
        required: true
        description: "Registers, then caches (L1, L2, L3; kilobytes to megabytes, a few nanoseconds), then RAM (gigabytes, about a hundred nanoseconds), then SSD and disk (microseconds to milliseconds): each level roughly ten times slower and far larger. Memory moves in cache lines of 64 bytes, so reading one float64 brings its seven neighbours into the cache."
      - id: layout
        required: true
        description: "An array is one block of bytes plus a shape and strides, the bytes to step along each axis; in C order the last axis is contiguous and element [i, j] sits at i times stride0 plus j times stride1. Slices and transposes are views (same block, different strides; np.shares_memory is True; writing through them changes the base); boolean and integer indexing copy."
      - id: locality
        required: true
        description: "In C order a row's elements are neighbours and a column's are a whole row apart, so walking by rows uses every byte of each cache line and walking by columns fetches a line for one element and evicts it before its neighbours are needed; a cache simulation shows the miss count multiplied by the floats per line (8 for float64)."
      - id: bytes-moved
        required: true
        description: "Simple operations (sum, add, copy) do one or two operations per byte, so memory bandwidth, not arithmetic, bounds their speed: memory-bound. Doubling the batch doubles the bytes to move, so such a step takes twice as long; only operations with many arithmetic steps per byte (matrix multiplies) gain from more compute."
    model_answer: |
      Memory is a ladder. At the top are the registers, the few values the processor is operating on right now. Below them are the caches, small fast copies of recently used memory: L1 is tens of kilobytes and about a nanosecond away, L2 a few hundred kilobytes and a few nanoseconds, L3 megabytes and ten or twenty nanoseconds. Below the caches is RAM, gigabytes, about a hundred nanoseconds away, and below that solid-state storage at around a hundred microseconds and spinning disk at milliseconds. Each step down is roughly ten times slower and far larger. Memory moves between RAM and the caches in cache lines of 64 bytes, so reading one eight-byte float brings its seven neighbours along, which is free if the code wants them next and wasted if it doesn't. A NumPy array is one flat block of bytes plus a shape and strides, where a stride is the number of bytes to step to the next element along an axis. In the default C order the last axis is contiguous: a 3 by 4 float64 array has strides of 32 and 8, and element [i, j] sits at 32 i plus 8 j bytes from the start. Transposing swaps the strides without touching the bytes, and slicing just changes the starting point and the strides, so both are views: they share memory with the original, np.shares_memory says so, and writing through them changes the original. Boolean and integer indexing can't be expressed with strides, so they copy, and writing into the copy changes nothing else. My second teammate was writing into a copy one time and a view the next; checking shares_memory would have told them which. The loop order mattered because of the lines: summing by rows walks the contiguous axis, so every byte of each 64-byte line fetched is used; summing by columns jumps a whole row at a time, fetches a line for one element and, with a cache smaller than the number of rows, evicts it before its neighbours are needed, so almost every element is a miss. A simulation of a small least-recently-used cache shows it: walking a 256 by 256 float64 matrix by rows through a 64-line cache misses 8,192 times, once per line, and by columns 65,536 times, once per element, eight times the memory traffic for the same arithmetic. That is also the answer about the batch size. A step like a sum, an add or a copy does one or two operations per byte, so its speed is bounded by how fast bytes can be moved, the memory bandwidth, not by how fast the processor can add. Doubling the batch doubles the bytes, so a memory-bound step takes twice as long. Only operations that do many arithmetic steps per byte they load, matrix multiplies above all, can use more compute instead, which is why they are the ones that get faster with a bigger batch or a bigger GPU.
review_pool:
  - review-predict-cache-misses
  - review-mcq-a-free-transpose
  - review-mcq-memory-bound
  - review-strides
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: hierarchy
    description: "Name the memory hierarchy's levels and rough costs, and say what a cache line is"
  - id: layout
    description: "Read an array's strides, and tell a view from a copy"
  - id: locality
    description: "Predict which loop order is cache-friendly, and show it by counting cache lines"
  - id: bytes-moved
    description: "Say why bytes moved bound a simple operation's speed"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    '''<Intro>

A processor can add two numbers in a nanosecond and wait a hundred of them for the numbers to arrive. Where a value sits, and what sits next to it, decides more about speed than the arithmetic does. This topic is the ladder of memory from registers to disk, the **cache line** that makes nearby bytes almost free, how NumPy lays an array out so that one loop order walks memory in sequence and the other jumps across it, which indexing operations share memory and which copy, and why the simplest operations are bounded by **bytes moved** rather than by the processor.

The main resource is **NumPy's user guide page on copies and views**, which says exactly which operations return a view of the same memory and which make a copy, with `base` to check (`np.shares_memory` is this topic's addition); about 15 minutes. The ndarray reference's section on internal memory layout has strides and C against Fortran order, and Wikipedia's _CPU cache_ article has the hierarchy and the line. Watch for:

- **`base`** and `np.shares_memory`: how to tell a view from a copy.
- **Basic indexing views, advanced indexing copies**: the rule in one line.
- **Cache misses** and why a miss costs a hundred hits.

</Intro>

<Resource index={0} />

<Recap>

- **The memory hierarchy.** **Registers** hold the few values being operated on. **Caches** (L1, L2, L3) are small, fast copies of recently used memory: tens of kilobytes about a nanosecond away, up to tens of megabytes a dozen or two away. **RAM** is gigabytes at roughly a hundred nanoseconds; **SSD** around a hundred microseconds; disk and network, milliseconds. Each step down is roughly ten times slower and far larger (the numbers are approximate and vary by machine; the shape of the ladder doesn't). Memory moves between RAM and the caches in **cache lines**, 64 bytes on common processors: reading one float64 brings its seven neighbours along.
- **How NumPy stores an array:** one flat block of bytes plus a **shape** and **strides**, the bytes to step along each axis. In the default **C order** (row-major) the last axis is contiguous: a `(3, 4)` float64 array has strides `(32, 8)`, and element `[i, j]` sits at `32 * i + 8 * j` bytes from the start; row 1 occupies bytes 32 to 63. `a.T` is the same block with strides swapped to `(8, 32)`: a **view**, free to make, but no longer **contiguous** (`a.flags["C_CONTIGUOUS"]` is `False`).
- **View or copy.** Slices and transposes are views: `a[:, ::2]` is the same block with strides `(32, 16)`, `np.shares_memory` is `True`, and writing through it changes `a`. Boolean and integer indexing (`a[a > 5]`, `a[[0, 2]]`) can't be described by strides, so they **copy**, and writing into the copy changes nothing else. `np.ascontiguousarray(a)` copies into a fresh contiguous block when a routine needs one.
- **Locality.** In C order a row's elements are neighbours and a column's are a whole row apart. Walking a matrix **by rows** uses every byte of each cache line; walking it **by columns** fetches a line for one element and, if the cache holds fewer lines than there are rows, evicts it before its neighbours are needed. The worked example's cache simulation (64 lines, least recently used) walks a 256 by 256 float64 matrix: 8,192 misses by rows, once per line; 65,536 by columns, once per element. Same arithmetic, eight times the memory traffic. `a.sum(axis=1)` walks rows; `a.sum(axis=0)` is written by NumPy to walk rows too, so prefer the library's reductions to your own loops.
- **Bytes moved.** A `(1000, 1000)` float64 array is 8,000,000 bytes. `grid.sum()` reads 8 MB; `grid + 1` reads 8 MB and writes 8 MB into a new block; `grid += 1` reads and writes the same block: about the same bytes moved, but no second block to allocate and half the peak memory. For such operations the processor does one or two steps per byte, so **memory bandwidth** (gigabytes per second between RAM and the processor) bounds the speed: they are **memory-bound**, and doubling the data doubles the time whatever the processor. Operations with many steps per byte, a matrix multiply above all, are **compute-bound**; the next topics are about them.
- **In machine learning** (names you'll meet later): a batch's layout (channels first or last) is chosen so the hot loop walks contiguous memory; PyTorch's `.contiguous()` is `ascontiguousarray`; a GPU has its own hierarchy (registers, shared memory, device memory) with the same shape; and most of a training step's time outside the matrix multiplies is memory-bound, which is why fusing operations, which moves the bytes once instead of three times, is a speed-up in its own right.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

mcq(
    "mcq-what-a-cache-line-is",
    "Reading a single float64 from RAM takes about a hundred nanoseconds; reading the float next to it right afterwards takes about one. Why?",
    [
        "Because the processor predicts the next address and fetches it in advance, which works for any access pattern, however scattered",
        "Because RAM is faster for the second access of any value, as the capacitors holding it are already charged from the first read",
        "Because NumPy keeps a copy of the last row it read in a Python list and serves the neighbour from there",
        "Because memory moves in 64-byte cache lines: the first read brought the whole line, neighbour included, into the cache",
    ],
    3,
    "RAM and the caches exchange fixed-size lines, 64 bytes on common processors, never single values. The first read paid the RAM latency (the wait before the first byte arrives) and copied the line, eight float64s, into the cache; the neighbour was already there. Prefetching exists but needs a pattern to predict; the line is why even a single miss helps its neighbours. RAM has no memory of what was read before, and NumPy keeps no Python-side copy of rows; the cache line is the whole explanation.",
    ["hierarchy"],
)

mcq(
    "mcq-the-latency-ladder",
    "Roughly how do the levels of the memory hierarchy compare, from the processor outwards?",
    [
        "Each level is roughly ten times slower and far larger than the one above: caches in nanoseconds, RAM in about a hundred, SSD in microseconds, disk in milliseconds",
        "Registers, cache, RAM and disk all take about the same time to reach; the only difference between them is how much each can hold, from a few bytes in a register up to terabytes on a disk",
        "RAM is the fastest level, which is why arrays are kept there, and the caches are slower backups for when RAM is full",
        "Disk is about twice as slow as RAM, which is why loading a dataset takes about twice as long as processing it",
    ],
    0,
    "The ladder's rungs are roughly a factor of ten apart in time and a factor of a hundred or more in size: a cache hit in nanoseconds, a RAM access in about a hundred, an SSD read in about a hundred microseconds, a disk seek in milliseconds. Caches are the fast levels, not backups. The exact numbers vary by machine; the orders of magnitude don't.",
    ["hierarchy"],
)

write(
    "recall/predict-strides.yaml",
    f'''id: predict-strides
type: predict_output
rev: 1
prompt: |
  The strides of a `(4, 5)` float32 array, its transpose, two slices of it, and a three-dimensional int16 array. What does the program print?
code: |
{block(PREDICT_STRIDES)}expected_output: |
{block(PREDICT_STRIDES_OUT)}explanation: |
  A float32 is 4 bytes, so stepping along a row is 4 bytes and stepping down a column is a whole row, 20. The transpose swaps the two. Taking every other row doubles the row stride to 40 and leaves the column stride alone; a column slice changes only where the view starts. For the int16 array, the last axis steps 2 bytes, the middle axis a row of 4 items (8), and the first axis a plane of 3 rows (24).
skills: [layout]
''',
)

write(
    "recall/predict-view-or-copy.yaml",
    f'''id: predict-view-or-copy
type: predict_output
rev: 1
prompt: |
  Four ways of taking part of an array, tested for shared memory, then written through. What does the program print?
code: |
{block(PREDICT_VIEWS)}expected_output: |
{block(PREDICT_VIEWS_OUT)}explanation: |
  A slice and a transpose are views: the same bytes with a different start or strides, so they share memory and writing 99 into `rows` changes `a[1, 0]`. A boolean mask picks elements that aren't evenly spaced, so NumPy copies them, and `copy()` copies by definition; writing 77 into `chosen` leaves `a[0, 0]` at 0.
skills: [layout]
''',
)

write(
    "recall/parsons-write-through-a-view.yaml",
    "id: parsons-write-through-a-view\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to set the whole first row of a zero matrix to 7 by writing through a view of it, and print `7.0 True`. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("top_row = a[0].copy()")
    + "\nexplanation: |\n"
    + block("`a[0]` is a view of the first row: the same bytes, so `top_row[:] = 7` writes into `a` and `shares_memory` is `True`. The decoy takes a copy, so the 7s land in a separate block and `a[0, 0]` stays 0.")
    + "skills: [layout]\n",
)

mcq(
    "mcq-which-loop-order",
    "A `(10000, 10000)` float64 matrix in C order is summed twice by hand-written loops: once row by row, once column by column. Which is faster, and why?",
    [
        "Column by column, because a column is one dimension and the processor handles one dimension at a time, loading it into the registers as a unit before it starts adding them up",
        "Neither; the same 100 million additions are done either way, and additions are what take the time",
        "Row by row: a row's elements are neighbours, so every cache line fetched is used in full; a column's are a whole row apart, so each fetch is mostly wasted",
        "Column by column, because NumPy stores arrays column by column underneath, whatever the shape says",
    ],
    2,
    "In C order the last axis is contiguous: stepping along a row moves 8 bytes, stepping down a column moves a whole row, 80,000 bytes. The additions are the same; the memory traffic is not. Walking rows uses all eight floats of each 64-byte line; walking columns fetches a line for one float, and with ten thousand rows the cache can't hold them all until the next column comes round, so nearly every element is a miss.",
    ["locality"],
)

mcq(
    "mcq-bytes-moved",
    "`grid` is a `(1000, 1000)` float64 array. Compare `grid = grid + 1` with `grid += 1` in terms of memory.",
    [
        "They are identical; Python rewrites the first into the second before NumPy sees either of them",
        "`grid + 1` fills a second 8 MB block; `grid += 1` reads and writes the same block: no new block, half the peak memory",
        "`grid += 1` is slower, because in-place operations have to lock the array while they run",
        "`grid + 1` is faster, because a fresh block is laid out contiguously and the old one may have been fragmented by earlier writes into it",
    ],
    1,
    "`grid + 1` allocates a second 8-megabyte block, reads every element of the first and writes every element of the second; `grid += 1` reads and writes the same block. Both forms read 8 MB and write 8 MB, so the bytes moved are about the same; what the in-place form saves is allocating and first touching a second block, which costs page faults and a read of each fresh line, and it keeps the peak memory at one copy instead of two. Python doesn't rewrite one into the other; NumPy implements `+=` as an in-place operation.",
    ["bytes-moved"],
)

write(
    "recall/review-predict-cache-misses.yaml",
    f'''id: review-predict-cache-misses
type: predict_output
rev: 1
prompt: |
  The cache simulator from the worked example on a 16 by 16 float64 matrix (8 floats per line): rows through a 2-line cache, columns through a 2-line cache, and columns through a 16-line cache. What does the program print?
code: |
{block(REVIEW_MISSES)}expected_output: |
{block(REVIEW_MISSES_OUT)}explanation: |
  By rows, each line is fetched once and its eight floats used in turn: 256 floats over 8 is 32 misses, whatever the cache size. By columns with only 2 lines, every element is in a different line from the last and the line is gone before its neighbours are wanted: 256 misses. With 16 lines the cache holds one line per row, so a column's lines stay until the next seven columns have used them: 32 again. Locality is about the cache being big enough for the pattern.
skills: [locality]
''',
)

mcq(
    "review-mcq-a-free-transpose",
    "`a.T` on a large array returns instantly, but a routine that is handed `a.T` runs slowly. What happened?",
    [
        "`a.T` copies the whole array in the background on a separate thread, and the routine has to wait for the copy to finish before it can start, which on a large array takes most of the time it is given",
        "Transposing a NumPy array is not allowed on large arrays, so the routine falls back to a Python loop over the elements",
        "The routine is slow for every input of that size; the transpose is a coincidence",
        "`a.T` only swaps the strides: free to make, but the routine now steps a whole row between neighbours and misses the cache; `np.ascontiguousarray` copies once into the order it wants",
    ],
    3,
    "Transposing swaps the strides and nothing else, which is why it is free and why the result isn't contiguous: the routine's inner loop now steps a whole row at a time and fetches a cache line per element. Copying into a contiguous block costs one pass over the bytes and makes every later pass walk in sequence; it is worth it when the routine will walk the array more than once.",
    ["layout"],
)

mcq(
    "review-mcq-memory-bound",
    "A function multiplies every element of a large float64 array by 2 and is memory-bound. Which change would make it faster?",
    [
        "A faster processor, since the multiplications are the work",
        "Letting NumPy use every core of the processor for the multiply, so the arithmetic is shared out",
        "Storing the array as float32 instead of float64, so half as many bytes move",
        "Reading the array once beforehand to warm the cache, so the multiply finds it there",
    ],
    2,
    "Memory-bound means the time is the bytes moved divided by the bandwidth; the processor is waiting, so a faster one changes nothing, and more cores only share arithmetic that wasn't the bottleneck while competing for the same bandwidth. float32 halves the bytes and so about halves the time, if its 7 digits are enough for the values. An array far bigger than the cache can't be warmed: the first pass evicts itself, and it is one more pass over the same bytes. (Writing the result in place saves a second block and the peak memory, but the array is still read and written once.)",
    ["bytes-moved"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-rows-columns-and-cache-lines/exercise.yaml",
    f'''id: example-rows-columns-and-cache-lines
stage: worked_example
rev: 1
title: "Rows, columns and cache lines"
prompt: |
  A small array's strides and where its elements sit, two ways of taking part of it that share memory and one that doesn't, a simulated cache walked by rows and by columns, and the bytes a large array's operations move. Press **Run**, then read how each part works.
steps:
  - label: "Strides: where each element sits"
    lines: "{ln('a = np.arange(12')}-{ln('a[1, 2] sits')}"
    note: "A `(3, 4)` float64 array is one block of 96 bytes with strides `(32, 8)`: step 8 bytes along a row, 32 down a column. Element `[1, 2]` sits at `32 + 16 = 48`, and row 1 is bytes 32 to 63. The transpose swaps the strides to `(8, 32)` without moving a byte, which is why it is no longer contiguous."
  - label: "A view and a copy"
    lines: "{ln('every_other_column = a[:, ::2]')}-{ln('after writing 100')}"
    note: "Every other column is a view: the same block with strides `(32, 16)`, so `shares_memory` is `True` and writing 100 through it changes `a[0, 0]`. The boolean mask picks scattered elements that no stride can describe, so NumPy copies them, and `shares_memory` is `False`."
  - label: "A cache you can count"
    lines: "{ln('def misses')}-{ln('    return count')}"
    note: "A model of a cache: `lines_in_cache` slots, each holding one 64-byte line of 8 float64s, least recently used evicted first (`OrderedDict` keeps the order). Walking the matrix by rows or by columns, every element's line is looked up; a miss costs a fetch and may evict the oldest line."
  - label: "By rows and by columns"
    lines: "{ln('for order in (')}-{ln('misses((256, 256), order, 64)')}"
    note: "By rows, each line is fetched once and all eight of its floats are used before the next line: 65,536 floats over 8 is 8,192 misses. By columns, each element is a row apart from the last, a different line every time, and with only 64 lines of cache for 256 rows the line is evicted before its neighbours come round: 65,536 misses, every element. Same arithmetic, eight times the traffic."
  - label: "Bytes moved"
    lines: "{ln('grid = np.zeros((1000, 1000)')}-{ln('grid + 1 made a new block')}"
    note: "A thousand by a thousand float64s is 8,000,000 bytes. `grid + 1` reads all of them and writes 8,000,000 more into a fresh block; `grid += 1` writes back into the same block. For an operation this simple, the bytes are the cost."
''',
)
write("exercises/example-rows-columns-and-cache-lines/solution.py", EXAMPLE)
write(
    "exercises/example-rows-columns-and-cache-lines/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the strides and offsets, the view and copy, the two miss counts and the bytes moved."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-strides-by-hand/exercise.yaml",
    f'''id: fill-strides-by-hand
stage: fill_in
rev: 1
title: "Strides by hand"
prompt: |
  `c_strides(shape, itemsize)` should compute the byte strides NumPy uses for a C-order array: the last axis steps one item, and each earlier axis steps the whole block of the axes after it. Replace each `...` so the program prints the strides of three arrays, matching what NumPy reports:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "The last axis's stride is the item size itself; start the running step there."
  - "Moving outwards, each axis's block is the previous step times the size of the axis just handled."
skills: [layout]
''',
)
write("exercises/fill-strides-by-hand/starter.py", FILL_STARTER)
write("exercises/fill-strides-by-hand/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-strides-by-hand/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three stride tuples."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_against_numpy():
    """Matches NumPy's strides for several shapes and item sizes, including one axis and four."""
    c_strides = function("c_strides")
    for shape in ((7,), (3, 4), (2, 3, 4), (2, 3, 4, 5)):
        for dtype in ("int16", "float32", "float64"):
            assert c_strides(shape, np.dtype(dtype).itemsize) == np.zeros(shape, dtype=dtype).strides
''',
)
write("exercises/fill-strides-by-hand/wrong/fortran-order.py", FILL_WRONG)
write(
    "exercises/fill-strides-by-hand/wrong/typed-in.py",
    "def c_strides(shape, itemsize):\n    return (32, 8)\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-a-cache-simulator/exercise.yaml",
    f'''id: write-a-cache-simulator
stage: write
rev: 1
title: "A cache you can count"
prompt: |
  Write `misses(shape, order, lines_in_cache, floats_per_line=8)`: walk a float64 matrix of that shape element by element, by `"rows"` (all of row 0, then row 1, ...) or by `"columns"`, through a cache that holds `lines_in_cache` cache lines and evicts the least recently used; an element's line is `(row, column // floats_per_line)`; count the misses. `collections.OrderedDict` keeps insertion order, `move_to_end` marks a line as just used, and `popitem(last=False)` drops the oldest. Then print:

  ```python
  for order in ("rows", "columns"):
      print(order, misses((128, 128), order, 32))
  print(misses((8, 8), "columns", 8))
  ```

  ```
{block(WRITE_OUT)}  ```

  By rows, every line is used fully: 128 × 128 / 8. By columns with 32 lines for 128 rows, every element misses. With a cache big enough for one line per row, columns cost no more than rows.
hints:
  - "On a hit, move the line to the end so it counts as recently used; on a miss, add it and, if the cache is now too big, pop the oldest from the front."
  - "The two visiting orders differ only in which loop is outer."
skills: [locality]
''',
)
write("exercises/write-a-cache-simulator/starter.py", "from collections import OrderedDict\n")
write("exercises/write-a-cache-simulator/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-a-cache-simulator/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the two orders and the small case."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_the_threshold():
    """On a 16 by 16 matrix by columns, a 15-line cache misses every element and a 16-line one misses once per line; by rows one line is enough."""
    misses = function("misses")
    assert misses((16, 16), "columns", 15) == 256 and misses((16, 16), "columns", 16) == 32
    assert misses((16, 16), "rows", 1) == 32
''',
)
write("exercises/write-a-cache-simulator/wrong/never-evicts.py", WRITE_WRONG)
write("exercises/write-a-cache-simulator/wrong/line-per-element.py", WRITE_LINE_PER_ELEMENT)
write(
    "exercises/write-a-cache-simulator/wrong/typed-in.py",
    "def misses(shape, order, lines_in_cache, floats_per_line=8):\n    return 2048\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-a-layout-toolkit/exercise.yaml",
    f'''id: build-a-layout-toolkit
stage: build
rev: 1
title: "A layout toolkit"
prompt: |
  Starting from a blank editor, write four functions:

  - `c_strides(shape, itemsize)`: the byte strides of a C-order array of that shape and item size.
  - `byte_offset(shape, itemsize, index)`: how many bytes from the start of such an array the element at `index` (a tuple) sits.
  - `misses(shape, order, lines_in_cache, floats_per_line=8)`: the cache simulator: a float64 matrix walked by `"rows"` or `"columns"` through a least-recently-used cache of that many lines, counting misses.
  - `traffic(shape, dtype, reads, writes)`: the bytes an operation moves if it reads the whole array `reads` times and writes it `writes` times (`np.dtype(dtype).itemsize` is the bytes per element).

  Then print:

  ```python
  print(c_strides((3, 4), 8), byte_offset((3, 4), 8, (1, 2)), byte_offset((2, 3, 4), 2, (1, 2, 3)))
  print(misses((256, 256), "rows", 64), misses((256, 256), "columns", 64))
  print(traffic((1000, 1000), "float64", 1, 0), traffic((1000, 1000), "float64", 1, 1), traffic((1000, 1000), "float32", 1, 1))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks compare the strides and offsets with real NumPy arrays, test the cache at the size where one line per row is the difference between a hit and a miss, and check the traffic for three dtypes.
skills: [layout, locality, bytes-moved]
''',
)
write("exercises/build-a-layout-toolkit/starter.py", "")
write("exercises/build-a-layout-toolkit/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-a-layout-toolkit/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the three lines."""
    assert run() == {BUILD_OUT!r}


def test_strides_and_offsets_against_numpy():
    """Strides match NumPy for four shapes and three dtypes, and the offset of an element is its stride-weighted index."""
    c_strides = function("c_strides")
    byte_offset = function("byte_offset")
    for shape in ((7,), (3, 4), (2, 3, 4), (2, 3, 4, 5)):
        for dtype in ("int16", "float32", "float64"):
            a = np.zeros(shape, dtype=dtype)
            assert c_strides(shape, a.itemsize) == a.strides
            last = tuple(size - 1 for size in shape)
            assert byte_offset(shape, a.itemsize, last) == sum(i * s for i, s in zip(last, a.strides))
    assert byte_offset((3, 4), 8, (0, 0)) == 0


def test_cache_eviction():
    """On a 16 by 16 matrix by columns, 15 lines miss every element and 16 lines miss once per line; by rows one line is enough."""
    misses = function("misses")
    assert misses((16, 16), "columns", 15) == 256 and misses((16, 16), "columns", 16) == 32
    assert misses((16, 16), "rows", 1) == 32 and misses((64, 64), "rows", 4) == 512


def test_traffic():
    """A million float32s read once and written once move 8,000,000 bytes; int16 read twice moves 4,000,000; an empty shape is one element."""
    traffic = function("traffic")
    assert traffic((1000, 1000), "float32", 1, 1) == 8_000_000
    assert traffic((1000, 1000), "int16", 2, 0) == 4_000_000
    assert traffic((), "float64", 1, 0) == 8
''',
)
write("exercises/build-a-layout-toolkit/wrong/fortran-strides.py", BUILD_FORTRAN_STRIDES)
write("exercises/build-a-layout-toolkit/wrong/never-evicts.py", BUILD_NO_EVICTION)
write("exercises/build-a-layout-toolkit/wrong/traffic-counts-elements.py", BUILD_TRAFFIC_ELEMENTS)
write(
    "exercises/build-a-layout-toolkit/wrong/typed-in.py",
    "def c_strides(shape, itemsize):\n    return (32, 8)\n\n\ndef byte_offset(shape, itemsize, index):\n    return 48\n\n\ndef misses(shape, order, lines_in_cache, floats_per_line=8):\n    return 8192\n\n\ndef traffic(shape, dtype, reads, writes):\n    return 8000000\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-an-offset-and-a-copy/exercise.yaml",
    f'''id: debug-an-offset-and-a-copy
stage: debug
rev: 1
title: "An offset and a copy"
prompt: |
  `byte_offset` should say where an element of a C-order array sits, and `clear_top_row` should zero the first row of an array in place. The program should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the offset of `[1, 2]` comes out as 40 against NumPy's 48, because the row is multiplied by the number of **rows** instead of the number of **columns**: stepping down one row skips a whole row of `cols` items. Fix that, and the first row is still `[0. 1. 2. 3.]` after clearing: `clear_top_row` zeroes a **copy** of the row, so `a` never sees it; a slice `a[0]` is a view, and writing through the view is what changes `a`.
skills: [layout]
''',
)
write("exercises/debug-an-offset-and-a-copy/starter.py", DEBUG_STARTER)
write("exercises/debug-an-offset-and-a-copy/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-an-offset-and-a-copy/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the matching offsets and a zeroed first row."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_other_shapes():
    """The offset matches NumPy's strides on a 5 by 7 float32 array, and clearing works on a 2 by 2 int32 array."""
    byte_offset = function("byte_offset")
    clear_top_row = function("clear_top_row")
    a = np.zeros((5, 7), dtype=np.float32)
    assert byte_offset(a.shape, a.itemsize, (3, 6)) == 3 * a.strides[0] + 6 * a.strides[1]
    b = np.ones((2, 2), dtype=np.int32)
    clear_top_row(b)
    assert b.tolist() == [[0, 0], [1, 1]]
''',
)
write("exercises/debug-an-offset-and-a-copy/wrong/still-wrong-axis.py", DEBUG_STILL_AXIS)
write("exercises/debug-an-offset-and-a-copy/wrong/still-a-copy.py", DEBUG_STILL_COPY)
write(
    "exercises/debug-an-offset-and-a-copy/wrong/typed-in.py",
    "import numpy as np\n\n\ndef byte_offset(shape, itemsize, index):\n    return 48\n\n\ndef clear_top_row(a):\n    pass\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-strides/exercise.yaml",
    f'''id: review-strides
stage: review_code
rev: 1
title: "Strides, from memory"
prompt: |
  Write `c_strides(shape, itemsize)`, the byte strides of a C-order array (the last axis steps one item, each earlier axis a whole block of the later ones), and print them for `(3, 4)` float64, `(4, 5)` float32 and `(2, 3, 4)` int16:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [layout]
''',
)
write("exercises/review-strides/starter.py", "")
write("exercises/review-strides/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-strides/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three stride tuples."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_against_numpy():
    """Matches NumPy for a one-axis and a four-axis array."""
    c_strides = function("c_strides")
    for shape in ((9,), (2, 3, 4, 5)):
        assert c_strides(shape, 8) == np.zeros(shape, dtype=np.float64).strides
''',
)
write("exercises/review-strides/wrong/fortran-order.py", FILL_WRONG)
write(
    "exercises/review-strides/wrong/typed-in.py",
    "def c_strides(shape, itemsize):\n    return (32, 8)\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.hw.memory-and-caches written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
