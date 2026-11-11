"""Writes the topic ml.hw.profiling (Module 7's seventh topic). Run from the
repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Profiles are read for their call counts, which are exact, and times appear
only in lines checked by shape; tracemalloc's byte counts differ between
64-bit CPython and 32-bit Pyodide, so they are checked by shape too. Files
are written as bytes with LF endings."""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.hw.profiling")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str) -> str:
    result = subprocess.run([sys.executable, "-W", "error", "-c", program], capture_output=True, text=True, check=True)
    return result.stdout.replace("\r\n", "\n")


def fails(program: str) -> str:
    result = subprocess.run([sys.executable, "-W", "error", "-c", program], capture_output=True, text=True)
    assert result.returncode != 0, "expected the program to fail"
    return result.stderr


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

EXAMPLE = '''import cProfile
import pstats
import tracemalloc

import numpy as np


def distance_squared(a, b):
    dx, dy = a[0] - b[0], a[1] - b[1]
    return dx * dx + dy * dy


def nearest(points, queries):
    """For each query, the index of the nearest point: every pair costs a call to distance_squared."""
    result = []
    for q in queries:
        best, best_d = -1, float("inf")
        for i, p in enumerate(points):
            d = distance_squared(p, q)
            if d < best_d:
                best, best_d = i, d
        result.append(best)
    return result


def make_points(n):
    return [((i * 7919) % 1000 / 1000, (i * 104729) % 1000 / 1000) for i in range(n)]


def profile(function, *args):
    """Run the function under cProfile and return its result and the profile's table."""
    profiler = cProfile.Profile()
    profiler.enable()
    result = function(*args)
    profiler.disable()
    return result, pstats.Stats(profiler)


def calls(stats, name):
    """How many times the function of that name ran: the table's rows are (file, line, name) -> (primitive calls, calls, own time, cumulative time, callers)."""
    return sum(row[1] for (file, line, func), row in stats.stats.items() if func == name)


def own_time(stats, name):
    return sum(row[2] for (file, line, func), row in stats.stats.items() if func == name)


APPEND = "<method 'append' of 'list' objects>"
points, queries = make_points(300), make_points(100)
answer, stats = profile(nearest, points, queries)
print(f"distance_squared: {calls(stats, 'distance_squared'):,} calls | nearest: {calls(stats, 'nearest')} call | list.append: {calls(stats, APPEND):,} calls")
print(f"distance_squared's own time is {own_time(stats, 'distance_squared') / stats.total_tt:.0%} of the profiled total")

_, doubled = profile(nearest, make_points(600), make_points(200))
print(f"doubling both inputs: {calls(doubled, 'distance_squared'):,} calls, {calls(doubled, 'distance_squared') / calls(stats, 'distance_squared'):.1f} times as many: the loop is quadratic")


def nearest_vectorized(points, queries):
    P, Q = np.array(points), np.array(queries)
    squared = ((Q[:, None, :] - P[None, :, :]) ** 2).sum(axis=2)
    return np.argmin(squared, axis=1).tolist()


fast, fast_stats = profile(nearest_vectorized, points, queries)
print(f"vectorized: {calls(fast_stats, 'distance_squared')} calls to distance_squared, same answers: {fast == answer}")

tracemalloc.start()
floats = [float(i) for i in range(100_000)]
_, list_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
array = np.arange(100_000, dtype=np.float64)
print(f"a list of 100,000 floats: {list_peak:,} bytes at peak | the array: {array.nbytes:,} bytes | the list took {list_peak / array.nbytes:.1f} times as much")
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert len(EX) == 5, EX
SHAPES = {
    1: r"distance_squared's own time is [0-9]+% of the profiled total",
    4: r"a list of 100,000 floats: [0-9,]+ bytes at peak \| the array: 800,000 bytes \| the list took [0-9]+\.[0-9] times as much",
}
EXACT = {i: line for i, line in enumerate(EX) if i not in SHAPES}
assert EX[0] == "distance_squared: 30,000 calls | nearest: 1 call | list.append: 100 calls", EX[0]
assert EX[2] == "doubling both inputs: 120,000 calls, 4.0 times as many: the loop is quadratic", EX[2]
assert EX[3] == "vectorized: 0 calls to distance_squared, same answers: True", EX[3]
for i, pattern in SHAPES.items():
    assert re.fullmatch(pattern, EX[i]), EX[i]
SHARE = int(EX[1].split("is ")[1].split("%")[0])
assert SHARE > 30, SHARE
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_COUNTS = '''import cProfile
import pstats


def square(x):
    return x * x


def sum_of_squares(n):
    total = 0
    for i in range(n):
        total += square(i)
    return total


profiler = cProfile.Profile()
profiler.enable()
sum_of_squares(1000)
sum_of_squares(10)
profiler.disable()
counts = {func: row[1] for (file, line, func), row in pstats.Stats(profiler).stats.items()}
print(counts["square"], counts["sum_of_squares"])
'''
PREDICT_COUNTS_OUT = out(PREDICT_COUNTS)
assert PREDICT_COUNTS_OUT == "1010 2\n", PREDICT_COUNTS_OUT

PREDICT_DOUBLING = '''def pairs(items):
    count = 0
    for a in items:
        for b in items:
            count += 1
    return count


def halvings(n):
    count = 0
    while n > 1:
        n //= 2
        count += 1
    return count


print(pairs(range(100)), pairs(range(200)), pairs(range(200)) / pairs(range(100)))
print(halvings(1024), halvings(2048), halvings(2048) - halvings(1024))
'''
PREDICT_DOUBLING_OUT = out(PREDICT_DOUBLING)
assert PREDICT_DOUBLING_OUT == "10000 40000 4.0\n10 11 1\n", PREDICT_DOUBLING_OUT

REVIEW_NESTED = '''import cProfile
import pstats


def leaf():
    return 1


def inner():
    return sum(leaf() for _ in range(4))


def outer():
    return inner() + inner() + inner()


profiler = cProfile.Profile()
profiler.enable()
outer()
outer()
profiler.disable()
counts = {func: row[1] for (file, line, func), row in pstats.Stats(profiler).stats.items()}
print(counts["leaf"], counts["inner"], counts["outer"])
'''
REVIEW_NESTED_OUT = out(REVIEW_NESTED)
assert REVIEW_NESTED_OUT == "24 6 2\n", REVIEW_NESTED_OUT

PARSONS_LINES = [
    "import tracemalloc",
    "tracemalloc.start()",
    "numbers = [float(i) for i in range(10_000)]",
    "current, peak = tracemalloc.get_traced_memory()",
    "tracemalloc.stop()",
    "print(tracemalloc.is_tracing(), peak >= current > 0)",
]
assert out("\n".join(PARSONS_LINES) + "\n") == "False True\n"

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''import cProfile
import pstats


def step(i):
    return i * 2


def work(n):
    return [step(i) for i in range(n)]


def calls_to(stats, name):
    """How many times the function called name ran, read from the profile's table; 0 if it never did."""
    for (file, line, func), (primitive, total, own, cumulative, callers) in stats.stats.items():
        if func == name:
            return total
    return 0


profiler = cProfile.Profile()
profiler.enable()
work(250)
profiler.disable()
stats = pstats.Stats(profiler)
print(calls_to(stats, "step"), calls_to(stats, "work"), calls_to(stats, "never"))
'''
FILL_STARTER = FILL_SOLUTION.replace("        if func == name:\n            return total\n", "        if func == ...:\n            return ...\n")
FILL_WRONG = FILL_SOLUTION.replace("            return total\n", "            return own\n")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "250 1 0\n", FILL_OUT
assert out(FILL_WRONG) != FILL_OUT


# --- a second fill-in: the biggest allocation ---------------------------------------------------

FILL_SNAPSHOT = '''import tracemalloc


def biggest_allocation(function):
    """Run the function under tracemalloc and return the line number and the bytes of the line that allocated the most."""
    tracemalloc.start()
    kept = function()
    snapshot = tracemalloc.take_snapshot()
    tracemalloc.stop()
    top = snapshot.statistics("lineno")[0]
    return top.traceback[0].lineno, top.size


def build():
    small = [float(i) for i in range(100)]
    big = [float(i) for i in range(100_000)]
    return small, big


line, size = biggest_allocation(build)
print(line == build.__code__.co_firstlineno + 2, size > 100_000 * 8)
'''
FILL_SNAPSHOT_STARTER = FILL_SNAPSHOT.replace('    top = snapshot.statistics("lineno")[0]', "    top = snapshot.statistics(...)[...]")
FILL_SNAPSHOT_WRONG = FILL_SNAPSHOT.replace('snapshot.statistics("lineno")[0]', 'snapshot.statistics("filename")[0]')
FILL_SNAPSHOT_OUT = out(FILL_SNAPSHOT)
assert FILL_SNAPSHOT_OUT == "True True\n", FILL_SNAPSHOT_OUT
assert out(FILL_SNAPSHOT_WRONG) != FILL_SNAPSHOT_OUT

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''import cProfile
import pstats


def heavy():
    total = 0
    for i in range(1_000_000):
        total += i * i
    return total


def light():
    total = 0
    for i in range(100):
        total += i
    return total


def run():
    for _ in range(500):
        light()
    return heavy()


def hot_spots(stats, k):
    """The names of the k functions with the most own time, largest first, leaving out the built-ins (their file is '~')."""
    rows = [(row[2], func) for (file, line, func), row in stats.stats.items() if file != "~"]
    rows.sort(reverse=True)
    return [func for own, func in rows[:k]]


profiler = cProfile.Profile()
profiler.enable()
run()
profiler.disable()
print(hot_spots(pstats.Stats(profiler), 2))
'''
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "['heavy', 'light']\n", WRITE_OUT
WRITE_BY_CUMULATIVE = WRITE_SOLUTION.replace("    rows = [(row[2], func)", "    rows = [(row[3], func)")
WRITE_BY_CALLS = WRITE_SOLUTION.replace("    rows = [(row[2], func)", "    rows = [(row[1], func)")
assert out(WRITE_BY_CUMULATIVE) != WRITE_OUT and out(WRITE_BY_CALLS) != WRITE_OUT

# --- the build ----------------------------------------------------------------------------------

BUILD_TOOLKIT = '''import cProfile
import pstats
import tracemalloc


def profile(function, *args):
    """Run the function under cProfile; return its result and the profile's table."""
    profiler = cProfile.Profile()
    profiler.enable()
    result = function(*args)
    profiler.disable()
    return result, pstats.Stats(profiler)


def call_counts(stats):
    """name -> how many times it ran, for the Python-level functions only (cProfile files the built-ins under '~')."""
    return {func: row[1] for (file, line, func), row in stats.stats.items() if file != "~"}


def hot_spots(stats, k):
    """The k Python-level functions with the most own time, largest first."""
    rows = [(row[2], func) for (file, line, func), row in stats.stats.items() if file != "~"]
    rows.sort(reverse=True)
    return [func for own, func in rows[:k]]


def peak_bytes(function, *args):
    """The most memory the function had allocated at any moment while it ran, in bytes."""
    tracemalloc.start()
    function(*args)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def growth(function, make_input, n, name):
    """How many times more often name is called when the input size doubles from n to 2n."""
    _, small = profile(function, make_input(n))
    _, large = profile(function, make_input(2 * n))
    return call_counts(large)[name] / call_counts(small)[name]
'''
BUILD_WORKLOAD = '''

def leaf(x):
    return x + 1


def branch(n):
    total = 0
    for i in range(n):
        total += leaf(i)
    return total


def root(n):
    return branch(n) + branch(n)


def pairs(items):
    total = 0
    for a in items:
        for b in items:
            total += leaf(a)
    return total


def tap():
    return 1


def grind(n):
    total = 0
    for i in range(n):
        total += i * i
    return total


def run():
    for _ in range(50):
        tap()
    return grind(100_000)


result, stats = profile(root, 1000)
counts = call_counts(stats)
print(result, counts["leaf"], counts["branch"], counts["root"], sorted(counts))
_, grind_stats = profile(run)
print(hot_spots(grind_stats, 1))
print(peak_bytes(lambda: [float(i) for i in range(50_000)]) > 50_000 * 8)
print(growth(branch, lambda n: n, 500, "leaf"), growth(pairs, lambda n: list(range(n)), 50, "leaf"))
'''
BUILD_SOLUTION = BUILD_TOOLKIT + BUILD_WORKLOAD
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == "1001000 2000 2 1 ['branch', 'leaf', 'root']\n['grind']\nTrue\n2.0 4.0\n", BUILD_OUT
BUILD_WITH_BUILTINS = BUILD_SOLUTION.replace("    return {func: row[1] for (file, line, func), row in stats.stats.items() if file != \"~\"}", "    return {func: row[1] for (file, line, func), row in stats.stats.items()}")
BUILD_BY_CUMULATIVE = BUILD_SOLUTION.replace("    rows = [(row[2], func) for (file, line, func), row in stats.stats.items() if file != \"~\"]", "    rows = [(row[3], func) for (file, line, func), row in stats.stats.items() if file != \"~\"]")
BUILD_CURRENT_NOT_PEAK = BUILD_SOLUTION.replace("    _, peak = tracemalloc.get_traced_memory()\n    tracemalloc.stop()\n    return peak", "    current, _ = tracemalloc.get_traced_memory()\n    tracemalloc.stop()\n    return current")
BUILD_NO_DOUBLING = BUILD_SOLUTION.replace("    _, large = profile(function, make_input(2 * n))", "    _, large = profile(function, make_input(n))")
for wrong in (BUILD_WITH_BUILTINS, BUILD_BY_CUMULATIVE, BUILD_CURRENT_NOT_PEAK, BUILD_NO_DOUBLING):
    assert wrong != BUILD_SOLUTION and out(wrong) != BUILD_OUT

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''import cProfile
import pstats


def heavy():
    total = 0
    for i in range(200_000):
        total += i * i
    return total


def light():
    return 1


def run():
    for _ in range(1_000):
        light()
    return heavy()


profiler = cProfile.Profile()
profiler.enable()
run()
profiler.disable()
stats = pstats.Stats(profiler)
rows = [(func, row[1], row[2]) for (file, line, func), row in stats.stats.items() if file != "~"]
rows.sort(key=lambda row: row[2], reverse=True)
print("most own time:", rows[0][0], "| calls to light:", next(count for func, count, own in rows if func == "light"))
'''
BUG_DISABLED_EARLY = ("profiler.enable()\nrun()\nprofiler.disable()", "profiler.enable()\nprofiler.disable()\nrun()")
BUG_BY_CALLS = ("rows.sort(key=lambda row: row[2], reverse=True)", "rows.sort(key=lambda row: row[1], reverse=True)")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_DISABLED_EARLY).replace(*BUG_BY_CALLS)
DEBUG_STILL_EARLY = DEBUG_SOLUTION.replace(*BUG_DISABLED_EARLY)
DEBUG_STILL_CALLS = DEBUG_SOLUTION.replace(*BUG_BY_CALLS)
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT)
assert DEBUG_OUT == "most own time: heavy | calls to light: 1000\n", DEBUG_OUT
assert "IndexError" in fails(DEBUG_STARTER)
assert out(DEBUG_STILL_CALLS) == "most own time: light | calls to light: 1000\n"

REVIEW_CODE_SOLUTION = FILL_SOLUTION
REVIEW_CODE_OUT = FILL_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.hw.profiling
kind: topic
status: ready
title: "Reading a profiler"
summary: "Finding where a program spends its time and memory: cProfile and pstats for calls and time, tracemalloc for allocations, the doubling test for growth, and the discipline of measuring before optimizing."
prerequisites: [ml.hw.vectorization]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Profile a program with cProfile, read the call counts and cumulative times in pstats, and find the hot spot."
  - "Measure peak memory and the biggest allocations with tracemalloc."
  - "Decide from a profile what to change first, change it, and show the profile after."
  - "Say why measuring beats guessing, and what a profiler's overhead does to small numbers."
# Linked, never copied or embedded: the Python documentation is under the PSF
# licence; Wikipedia is CC BY-SA 4.0.
resources:
  # Pinned to the 3.14 docs: the 3.15 docs split this page and moved cProfile.
  - title: "The Python standard library: The Python Profilers (cProfile, and reading a pstats table: ncalls, tottime, cumtime)"
    url: https://docs.python.org/3.14/library/profile.html
    type: reading
    use: link
    license: "PSF licence (linked, not copied)"
  - title: "The Python standard library: tracemalloc (get_traced_memory for current and peak bytes, and snapshots for where they were allocated)"
    url: https://docs.python.org/3/library/tracemalloc.html
    type: reading
    use: link
    license: "PSF licence (linked, not copied)"
  - title: "Wikipedia: Profiling (computer programming) (what profilers measure and the kinds there are)"
    url: https://en.wikipedia.org/wiki/Profiling_(computer_programming)
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
practice:
  - example-profile-a-nearest-neighbour-search
  - predict-call-counts
  - mcq-reading-the-columns
  - parsons-peak-memory
  - fill-the-biggest-allocation
  - mcq-current-and-peak
  - predict-the-doubling-test-by-counting
  - mcq-what-to-change-first
  - mcq-the-profiler-overhead
  - fill-calls-to
  - write-hot-spots
prove:
  build: build-a-profiling-toolkit
  debug: debug-a-profile-that-lied
  explain:
    prompt: |
      A teammate spent a day making a function faster and the program is no quicker; another ran a tiny helper under cProfile, saw it take a tenth of a second across a million calls, and wants to rewrite it in C; a third's training script grows to several gigabytes and they don't know where. In your own words: how you profile a program with cProfile, what the columns of a pstats table mean and which one you sort by to find the hot spot; how tracemalloc finds peak memory and where it was allocated; how you decide from a profile what to change first and how you show the change worked; and why measuring beats guessing, with what the profiler's own overhead does to the numbers for small functions.
    rubric:
      - id: cprofile
        required: true
        description: "Run the code under cProfile.Profile (or cProfile.run) and read the table with pstats: ncalls is how often a function ran, tottime its own time excluding callees, cumtime its time including callees. Sort by cumtime to see where the time goes, by tottime to find the function doing the work; the hot spot is usually one function with a huge call count or a huge own time."
      - id: tracemalloc
        required: true
        description: "tracemalloc.start() then get_traced_memory() gives the current and the peak bytes allocated since the start; a snapshot's statistics by line show which lines allocated the most. Peak is the number that decides whether a run fits."
      - id: decide
        required: true
        description: "Change the thing the profile points at, usually the one function that holds most of the time, by removing calls (vectorizing, caching, a better algorithm) rather than shaving each call; then profile again and show the calls gone or the share dropped, with the answers unchanged. The doubling test on counts shows the order."
      - id: measure
        required: true
        description: "Guesses about where time goes are usually wrong, and the hot spot is usually one place. cProfile adds a fixed cost to every call, so tiny functions called millions of times look far worse under the profiler than they are; read shares, not absolute times, and confirm with a timing outside the profiler before rewriting."
    model_answer: |
      To profile, I run the program under cProfile, either cProfile.run on a statement or a Profile object enabled around the code, and read the result with pstats. Each row of the table is one function. ncalls is how many times it ran, tottime is the time spent in its own body with the time of the functions it called taken out, cumtime is its time including everything it called, and percall is each of those divided by the calls. Sorting by cumtime shows where the time goes from the top down, which usually leads from main to one function; sorting by tottime shows which function's own body is doing the work. The hot spot is nearly always one row with a huge call count or a huge own time, and the first teammate's day was probably spent on a function that wasn't it; the profile would have shown that in a minute, and it is why the rule is to measure first. For memory, tracemalloc.start() begins tracing allocations, get_traced_memory() returns the bytes currently allocated and the peak since the start, and take_snapshot().statistics('lineno') lists the lines that allocated the most. Peak is the number that decides whether a run fits in memory. The third teammate should wrap the training step in it and read the top lines: the usual answers are a list that is never cleared, activations kept past the step, or a copy of the data made every iteration. Deciding what to change first means taking the row the profile points at and removing its calls rather than speeding each one up: a function called a hundred thousand times is replaced by one array operation, a repeated computation is cached, a quadratic loop gets a better algorithm. Then I profile again and show the evidence: the function's calls gone or its share dropped, and the answers unchanged. The doubling test on counts, calls at n and at 2n, says whether the loop is linear or quadratic, which tells me whether a bigger input will be fine or four times worse. Measuring beats guessing because the guess is usually wrong and the profile is cheap; it also keeps the fix honest, since the same profile run afterwards either shows the improvement or doesn't. The one thing to know about the profiler is that it adds a fixed cost to every function call, so a tiny function called a million times looks far slower under cProfile than it is in the real program. The second teammate's tenth of a second is mostly the profiler's own overhead; the right reading is the function's share of the whole, and the right next step is a timing without the profiler, which will probably show nothing worth rewriting.
review_pool:
  - review-mcq-why-measure
  - review-mcq-after-the-fix
  - review-predict-nested-calls
  - review-calls-to-from-memory
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: cprofile
    description: "Profile with cProfile and read a pstats table: calls, own time, cumulative time, the hot spot"
  - id: tracemalloc
    description: "Measure peak memory and the biggest allocations with tracemalloc"
  - id: decide
    description: "Decide from a profile what to change first, and show the profile after"
  - id: measure
    description: "Say why measuring beats guessing, and what the profiler's overhead does to small numbers"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    '''<Intro>

Everything in this module so far says what things cost in principle. This topic is about finding out what a particular program costs in fact, which is nearly always different from what its author thinks. A **profiler** runs the program and records, for every function, how often it was called and how long it took; a memory tracer records what was allocated and where. Reading those two tables is the skill, and the discipline that goes with it is simple: **measure before you optimize, and measure again after**.

The main resource is **the Python standard library's page on the profilers**: how to run cProfile and how to read the table that pstats prints, column by column; about 20 minutes. The tracemalloc page covers current and peak memory and the snapshot that says which lines allocated the most, and Wikipedia's _Profiling_ article says what kinds of profiler exist. Watch for:

- **`ncalls`, `tottime`, `cumtime`**: calls, own time, and time including callees.
- **`sort_stats`**: by cumulative time to see where the time goes, by own time to see who does the work.
- **`get_traced_memory`**: the current and the peak.

</Intro>

<Resource index={0} />

<Recap>

- **Running cProfile.** `cProfile.run("main()")` prints a table; for a piece of code, make a `cProfile.Profile()`, `enable()` it, run, `disable()` it, and read it with `pstats.Stats`. The table has a row per function: `ncalls` (how many times it ran), `tottime` (time in its own body, with the functions it calls, its callees, excluded), `percall`, `cumtime` (time including everything it called), and the file and line. The same numbers are in `Stats.stats`, a dictionary from `(file, line, name)` to `(primitive calls, calls, own time, cumulative time, callers)`, which is how the worked example reads them in code; built-in functions are filed under `'~'`.
- **Finding the hot spot.** Sort by `cumtime` and read from the top: the time flows from the entry point down to one or two functions that hold most of it. Sort by `tottime` to see whose body is doing the work. In the worked example `nearest` holds all the cumulative time and `distance_squared`, called 30,000 times, holds about half of the own time and `nearest`'s own loop the other half: the hot spot is the call count, not the function's body.
- **Counts are exact, times are not.** Two runs of the same program give the same `ncalls` and different times; the browser's clock is coarse and the machine is shared. So the proofs in this topic read call counts and shares, and the **doubling test on counts** replaces the one on times: doubling both inputs took `distance_squared` from 30,000 calls to 120,000, four times, so the loop is quadratic.
- **tracemalloc.** `tracemalloc.start()` begins tracing every allocation; `get_traced_memory()` returns `(current, peak)` in bytes, where peak is the high-water mark since the start, the number that decides whether a run fits; `take_snapshot().statistics("lineno")` lists the lines that allocated the most, which is where the gigabytes went. A list of 100,000 Python floats is several times the bytes of the same numbers in a NumPy array, because every float is an object with a header and the list holds a pointer to each (the exact bytes differ between a 64-bit machine and the browser's 32-bit one).
- **Deciding what to change.** Change what the profile points at, and prefer removing calls to speeding up each one: 30,000 calls to a small function become one array operation, a repeated computation gets cached, a quadratic loop gets a better algorithm (Module 6). Then **profile again and show the evidence**: the calls gone (`distance_squared`: 0), the share dropped, and the answers unchanged. A fix that can't be shown in the second profile didn't happen.
- **Why measure.** Guesses about where time goes are usually wrong, and the hot spot is usually one place; a profile takes a minute and settles it. The profiler has a cost of its own: cProfile adds a fixed overhead to every function call, so a tiny function called a million times looks far worse under the profiler than in the real program. Read shares, not absolute times, and confirm anything surprising with a timing outside the profiler (`time.perf_counter` around the call, or `timeit`) before rewriting it.
- **In machine learning** (names you'll meet later): the PyTorch profiler and NVIDIA's Nsight do the same job for GPU kernels, showing which ones hold the time and whether the GPU is waiting on the CPU; a training script's first profile usually shows the data loader or a per-example Python loop, not the model; peak memory from the framework's allocator (`torch.cuda.max_memory_allocated`) is tracemalloc's peak for the GPU; and "the step got faster" is a claim that needs a before and an after.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/predict-call-counts.yaml",
    f'''id: predict-call-counts
type: predict_output
rev: 1
prompt: |
  A function profiled under cProfile, and its call counts read from the table. What does the program print?
code: |
{block(PREDICT_COUNTS)}expected_output: |
{block(PREDICT_COUNTS_OUT)}explanation: |
  `sum_of_squares` ran twice, once for 1,000 and once for 10, and each run called `square` once per iteration: 1,010 calls in all. The table's value for each function is `(primitive calls, calls, own time, cumulative time, callers)`, so `row[1]` is the call count, which is exact; the times in the same row would differ from run to run.
skills: [cprofile]
''',
)

mcq(
    "mcq-reading-the-columns",
    "In a pstats table, what do `tottime` and `cumtime` mean, and which do you sort by to find where a program's time goes?",
    [
        "`tottime` is the total run time and `cumtime` the time since the program started; sort by `ncalls`",
        "`tottime` is wall-clock time and `cumtime` is CPU time; sort by `percall` to find the slowest single call, which is always the function to rewrite first, whatever the counts say",
        "They are the same number, measured twice to check the profiler; sort by either",
        "`tottime` is own time with callees excluded, `cumtime` includes them; sort by `cumtime` to follow the time down, by `tottime` to see who does the work",
    ],
    3,
    "Own time against inclusive time is the whole trick of reading a profile. `cumtime` sorted high to low reads like a map from the entry point to the function holding most of the time; `tottime` says which function's own body is busy, which is where a rewrite would go. `ncalls` is the count, and a huge count on a small function is the other shape a hot spot takes; `percall` is a division of the other two.",
    ["cprofile"],
)

write(
    "recall/parsons-peak-memory.yaml",
    "id: parsons-peak-memory\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to measure the memory a list of ten thousand floats takes with tracemalloc and print `False True`: tracing has stopped, and the peak is at least the current, which is above zero. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("current, peak = tracemalloc.get_tracemalloc_memory()")
    + "\nexplanation: |\n"
    + block("Tracing has to start before the allocation and the numbers have to be read before it stops. `get_traced_memory` returns the bytes allocated right now and the peak since the start, so the peak is at least the current and both are above zero while the list is alive; `is_tracing` is `False` only once `stop` has run, which is why the print comes last. The decoy, `get_tracemalloc_memory`, returns the memory the tracer itself is using, a single number that can't be unpacked into two.")
    + "skills: [tracemalloc]\n",
)

mcq(
    "mcq-current-and-peak",
    "`tracemalloc.get_traced_memory()` returns two numbers. What are they, and which one says whether a run will fit in memory?",
    [
        "The bytes allocated by Python and the bytes allocated by NumPy; their sum decides",
        "The memory of the current function and of its caller; the caller's decides",
        "The bytes allocated right now, and the most allocated at any moment since tracing began; the peak decides",
        "The bytes allocated and the bytes freed since tracing started; their difference decides, since what was freed is available again",
    ],
    2,
    "Current is what is allocated at the moment of the call; peak is the high-water mark, which may have been reached by something already freed. A run that frees its big arrays before the end can show a small current and a huge peak, and it is the peak that has to fit. Python and NumPy allocations are both traced, and there is no separate count of frees.",
    ["tracemalloc"],
)

write(
    "recall/predict-the-doubling-test-by-counting.yaml",
    f'''id: predict-the-doubling-test-by-counting
type: predict_output
rev: 1
prompt: |
  The doubling test on counts: how a nested loop and a halving loop grow when their input doubles. What does the program print?
code: |
{block(PREDICT_DOUBLING)}expected_output: |
{block(PREDICT_DOUBLING_OUT)}explanation: |
  `pairs` visits every pair, so 100 items is 10,000 steps and 200 is 40,000: four times for a doubled input, quadratic. `halvings` divides by two until it reaches 1: ten times from 1,024 and eleven from 2,048, one more step for a doubled input, logarithmic. Counting is the doubling test with the clock taken out: the same answer every run, on any machine.
skills: [decide]
''',
)

mcq(
    "mcq-what-to-change-first",
    "A profile shows one function with 85 percent of the own time, called 200,000 times from a loop, and a dozen others sharing the rest. What do you change first?",
    [
        "The loop making the 200,000 calls: replace them with one array operation, a cache or a better algorithm, then profile again",
        "The one function's body, to make each of the 200,000 calls a little faster, since a small saving multiplied by 200,000 is where the time is",
        "The dozen others, since there are more of them to improve",
        "Nothing yet: profile the dozen others individually first",
    ],
    0,
    "The profile points at one place, and a huge call count on a small function says the cost is the calls, not the body. Removing the calls (vectorizing the loop, caching repeated work, a better algorithm) can take the 85 percent to nothing; shaving the body takes it to 80. The dozen others share 15 percent between them, so nothing done to them matters yet. The second profile is the proof.",
    ["decide"],
)

mcq(
    "mcq-the-profiler-overhead",
    "Under cProfile, a one-line helper called a million times shows 0.4 seconds of own time. Without the profiler the whole program takes 0.3 seconds. What happened?",
    [
        "The profiler found a bug: the helper is slower than the whole program, so it must also be running in the background between calls, which the plain run doesn't show at all",
        "The helper allocates memory that the profiler has to free, which the plain run skips",
        "The two runs used different inputs; profiling changes the random seed",
        "cProfile adds a fixed cost to every call, so a tiny function called a million times looks far slower than it is; read its share and time it outside the profiler",
    ],
    3,
    "A profiler intercepts every call and return, and that costs a few hundred nanoseconds each time. For a function whose own work is a few nanoseconds, the overhead is the measurement. Shares between functions are still roughly right, which is what the profile is for; absolute times for tiny, hot functions are not. `time.perf_counter` around the program, without the profiler, is the number to believe.",
    ["measure"],
)

mcq(
    "review-mcq-why-measure",
    "A teammate is sure the slow part of a pipeline is the JSON parsing and wants to spend the week on it. What should happen first?",
    [
        "Rewrite the parsing in C, since parsing is always the slow part",
        "Add timing prints to every function, which is more precise than a profiler",
        "Profile one run first: it takes a minute, the hot spot is usually one place, and guesses about which place are usually wrong",
        "Double the input and see whether the run takes twice as long, which says where the time goes and so which function to work on first",
    ],
    2,
    "A profile costs almost nothing and settles the question; a week spent on the wrong function costs a week. The doubling test says how the time grows, not where it is spent, and timing prints are a hand-rolled profiler with worse coverage. If the parsing is the hot spot, the profile will say so, and the same profile afterwards will show whether the week worked.",
    ["measure"],
)

mcq(
    "review-mcq-after-the-fix",
    "You vectorized the hot loop of a nearest-neighbour search. What shows that the fix worked?",
    [
        "The code is shorter, and NumPy is known to be fast",
        "The doubling test gives a ratio below 2, showing the loop is now sub-linear, which is the signature of a properly vectorized operation",
        "The program prints its result faster the first time you run it",
        "A second profile with no calls to the per-pair function and less total time, with the answers unchanged on the same input",
    ],
    3,
    "The claim is about this program, so the evidence is this program's profile, before and after: the calls to the per-pair function gone, the share or total time down, and the same answers, since a fast wrong answer is not a fix. A single timing is noise; a vectorized search still computes every pair, so it stays quadratic in the number of points and the doubling ratio stays near 4 while the constant falls.",
    ["decide"],
)

write(
    "recall/review-predict-nested-calls.yaml",
    f'''id: review-predict-nested-calls
type: predict_output
rev: 1
prompt: |
  Three functions that call each other, profiled, with their call counts read from the table. What does the program print?
code: |
{block(REVIEW_NESTED)}expected_output: |
{block(REVIEW_NESTED_OUT)}explanation: |
  `outer` ran twice; each run calls `inner` three times, six in all; each `inner` calls `leaf` four times, twenty-four in all. The counts multiply down the call tree, which is why a cheap function at the bottom of two nested loops can hold most of a program's time.
skills: [cprofile]
''',
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-profile-a-nearest-neighbour-search/exercise.yaml",
    f'''id: example-profile-a-nearest-neighbour-search
stage: worked_example
rev: 1
title: "Profile a nearest-neighbour search"
prompt: |
  A nearest-neighbour search profiled with cProfile and read through pstats: the call counts, the hot function's share of the time, the doubling test on counts, the same search vectorized and profiled again, and the memory of a list against an array under tracemalloc. Press **Run**, then read how each part works. The share and the byte counts are measured on your machine and will differ from anyone else's.
steps:
  - label: "A search with a call per pair"
    lines: "{ln('def distance_squared')}-{ln('return [((i * 7919)')}"
    note: "`nearest` compares every query with every point, and each comparison is a call to `distance_squared`: 100 queries by 300 points is 30,000 calls. It compares squared distances, since the nearest point is the same either way and the square root is wasted work."
  - label: "Profiling in code"
    lines: "{ln('def profile(function')}-{ln('return sum(row[2]')}"
    note: "A `cProfile.Profile` is enabled around the call and read with `pstats.Stats`. Its `stats` dictionary maps `(file, line, name)` to `(primitive calls, calls, own time, cumulative time, callers)`, which is the same table `print_stats` would print, so a program can read its own profile: `calls` picks the call count and `own_time` the time in the function's own body."
  - label: "Counts, a share, and the doubling test"
    lines: "{ln('APPEND = ')}-{ln('doubling both inputs')}"
    note: "The counts are exact: 30,000 calls to `distance_squared`, one to `nearest`, 100 to the list's `append`. The share is a time, so it varies by machine, but it says the same thing everywhere: about half of the profiled time is inside the small function called 30,000 times, and the rest is in the loop that calls it. Doubling both inputs makes 120,000 calls, four times as many: the loop is quadratic, and a bigger input will be four times worse."
  - label: "Change what the profile points at, and profile again"
    lines: "{ln('def nearest_vectorized')}-{ln('vectorized: ')}"
    note: "The fix is to remove the calls, not to speed each one up: broadcasting computes all the squared distances in one operation and `argmin` picks the nearest. The second profile is the proof: `distance_squared` is called zero times, and the answers are the same."
  - label: "Memory: a list against an array"
    lines: "{ln('tracemalloc.start()')}-{ln('a list of 100,000 floats')}"
    note: "`tracemalloc` traces allocations between `start` and `stop`; `get_traced_memory` returns the current bytes and the peak. A list of 100,000 Python floats is several times the 800,000 bytes of the same numbers in a NumPy array, because every float is an object with a header and the list holds a pointer to each. The exact bytes differ by machine (the browser's Python is 32-bit); the ratio is the lesson."
''',
)
write("exercises/example-profile-a-nearest-neighbour-search/solution.py", EXAMPLE)
write(
    "exercises/example-profile-a-nearest-neighbour-search/test_exercise.py",
    f'''import re

from checks import run

EXACT = {EXACT!r}
# The share and the byte counts vary by machine, so those lines are checked by shape.
SHAPES = {SHAPES!r}


def test_the_walkthrough():
    """Prints the counts, a share, the doubling test, the vectorized profile and the memory comparison."""
    lines = run().splitlines()
    assert len(lines) == 5, lines
    for i, text in EXACT.items():
        assert lines[i] == text, lines[i]
    for i, pattern in SHAPES.items():
        assert re.fullmatch(pattern, lines[i]), lines[i]
''',
)

write(
    "exercises/fill-calls-to/exercise.yaml",
    f'''id: fill-calls-to
stage: fill_in
rev: 1
title: "Read a call count from the table"
prompt: |
  `calls_to(stats, name)` should return how many times the function called `name` ran, read from `stats.stats`, whose keys are `(file, line, name)` and whose values are `(primitive calls, total calls, own time, cumulative time, callers)`; 0 if the function never ran. Replace each `...` so the program prints:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "The loop unpacks each key into `file, line, func` and each value into five names; compare `func` with the name you were given."
  - "Return the total call count, the second value; the times are what change from run to run."
skills: [cprofile]
''',
)
write("exercises/fill-calls-to/starter.py", FILL_STARTER)
write("exercises/fill-calls-to/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-calls-to/test_exercise.py",
    f'''import cProfile
import pstats

from checks import function, run


def test_the_output():
    """Prints the three counts."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_another_profile():
    """Counts a function called 7 times, one called once, and one never called."""
    calls_to = function("calls_to")

    def seven():
        return 1

    def once():
        return sum(seven() for _ in range(7))

    profiler = cProfile.Profile()
    profiler.enable()
    once()
    profiler.disable()
    stats = pstats.Stats(profiler)
    assert calls_to(stats, "seven") == 7 and calls_to(stats, "once") == 1 and calls_to(stats, "never") == 0
''',
)
write("exercises/fill-calls-to/wrong/returns-a-time.py", FILL_WRONG)

write(
    "exercises/fill-the-biggest-allocation/exercise.yaml",
    f'''id: fill-the-biggest-allocation
stage: fill_in
rev: 1
title: "The biggest allocation"
prompt: |
  `biggest_allocation(function)` should run the function under tracemalloc, take a snapshot while what the function built is still alive (it returns its lists, and `kept` holds them), and return the line number and the bytes of the line that allocated the most. A snapshot's `statistics` groups the allocations by a key, `"lineno"` for a line of code, and returns them largest first; each statistic has a `traceback` whose first frame has the `lineno`, and a `size`. Replace each `...` so the program prints:

  ```
{block(FILL_SNAPSHOT_OUT)}  ```

  The first `True` says the top line is the one that builds the big list (two lines below `def build():`); the second says it allocated more than 100,000 floats' worth of bytes. The program fails until every `...` is replaced.
hints:
  - "The key is the string lineno, in quotes; filename would lump every line of the file together."
  - "The statistics come back sorted largest first, so the biggest is at index 0."
skills: [tracemalloc]
''',
)
write("exercises/fill-the-biggest-allocation/starter.py", FILL_SNAPSHOT_STARTER)
write("exercises/fill-the-biggest-allocation/solution.py", FILL_SNAPSHOT)
write(
    "exercises/fill-the-biggest-allocation/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints True True."""
    printed = run()
    assert printed == {FILL_SNAPSHOT_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_another_function():
    """Finds the line that builds the big list in two functions, with a size above the floats' own bytes."""
    biggest_allocation = function("biggest_allocation")

    def work():
        tiny = [0.0] * 10
        huge = [float(i) for i in range(50_000)]
        return tiny, huge

    line, size = biggest_allocation(work)
    assert line == work.__code__.co_firstlineno + 2 and size > 50_000 * 8

    def other():
        huge = [float(i) for i in range(40_000)]
        tiny = [0.0] * 10
        return huge, tiny

    line, size = biggest_allocation(other)
    assert line == other.__code__.co_firstlineno + 1 and size > 40_000 * 8
''',
)
write("exercises/fill-the-biggest-allocation/wrong/by-filename.py", FILL_SNAPSHOT_WRONG)
write(
    "exercises/fill-the-biggest-allocation/wrong/typed-in.py",
    "def biggest_allocation(function):\n    return 1, 10**7\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_SNAPSHOT_OUT.splitlines()),
)
write(
    "exercises/fill-calls-to/wrong/typed-in.py",
    "def calls_to(stats, name):\n    return 250\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-hot-spots/exercise.yaml",
    f'''id: write-hot-spots
stage: write
rev: 1
title: "The hot spots"
prompt: |
  The starter profiles `run`, which calls `light` 500 times and `heavy` once. Write `hot_spots(stats, k)`: the names of the `k` functions with the most **own** time, largest first, leaving out the built-ins (cProfile files those under a file name of `'~'`). `stats.stats` maps `(file, line, name)` to `(primitive calls, calls, own time, cumulative time, callers)`. The program prints:

  ```
{block(WRITE_OUT)}  ```
hints:
  - "Build a list of `(own time, name)` pairs for the rows whose file isn't `'~'`, sort it in reverse, and take the first `k` names."
  - "Own time is the third value of each row; cumulative time, the fourth, would put `run` first, since it includes everything it called."
skills: [cprofile]
''',
)
write("exercises/write-hot-spots/starter.py", WRITE_SOLUTION.split("def hot_spots")[0] + "profiler" + WRITE_SOLUTION.split("\nprofiler", 1)[1])
write("exercises/write-hot-spots/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-hot-spots/test_exercise.py",
    f'''import cProfile
import pstats

from checks import function, run


def test_the_output():
    """Prints the two hot spots in order."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_another_profile():
    """A function that loops a million times outranks one that loops 50,000 times, and the built-ins stay out of the list."""
    hot_spots = function("hot_spots")

    def alpha():
        total = 0
        for i in range(1_000_000):
            total += i
        return total

    def beta():
        total = 0
        for i in range(50_000):
            total += i
        return total

    def both():
        beta()
        return alpha()

    profiler = cProfile.Profile()
    profiler.enable()
    both()
    profiler.disable()
    stats = pstats.Stats(profiler)
    assert hot_spots(stats, 1) == ["alpha"] and hot_spots(stats, 2) == ["alpha", "beta"]
    assert all(not name.startswith("<") for name in hot_spots(stats, 10))
''',
)
write("exercises/write-hot-spots/wrong/by-cumulative-time.py", WRITE_BY_CUMULATIVE)
write("exercises/write-hot-spots/wrong/by-calls.py", WRITE_BY_CALLS)
write(
    "exercises/write-hot-spots/wrong/typed-in.py",
    "def hot_spots(stats, k):\n    return ['heavy', 'light']\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-a-profiling-toolkit/exercise.yaml",
    f'''id: build-a-profiling-toolkit
stage: build
rev: 1
title: "A profiling toolkit"
prompt: |
  Starting from a blank editor, write five functions:

  - `profile(function, *args)`: run the function under `cProfile.Profile` and return `(its result, pstats.Stats(profiler))`.
  - `call_counts(stats)`: a dictionary from function name to how many times it ran, for the Python-level functions only (cProfile files the built-ins under a file name of `'~'`).
  - `hot_spots(stats, k)`: the names of the `k` Python-level functions with the most own time, largest first.
  - `peak_bytes(function, *args)`: the peak memory, in bytes, that tracemalloc saw while the function ran.
  - `growth(function, make_input, n, name)`: how many times more often `name` is called when `function` runs on `make_input(2 * n)` than on `make_input(n)`: the doubling test on counts.

  `stats.stats` maps `(file, line, name)` to `(primitive calls, calls, own time, cumulative time, callers)`. Then paste this workload and print:

  ```python
  def leaf(x):
      return x + 1


  def branch(n):
      total = 0
      for i in range(n):
          total += leaf(i)
      return total


  def root(n):
      return branch(n) + branch(n)


  def pairs(items):
      total = 0
      for a in items:
          for b in items:
              total += leaf(a)
      return total


  def tap():
      return 1


  def grind(n):
      total = 0
      for i in range(n):
          total += i * i
      return total


  def run():
      for _ in range(50):
          tap()
      return grind(100_000)


  result, stats = profile(root, 1000)
  counts = call_counts(stats)
  print(result, counts["leaf"], counts["branch"], counts["root"], sorted(counts))
  _, grind_stats = profile(run)
  print(hot_spots(grind_stats, 1))
  print(peak_bytes(lambda: [float(i) for i in range(50_000)]) > 50_000 * 8)
  print(growth(branch, lambda n: n, 500, "leaf"), growth(pairs, lambda n: list(range(n)), 50, "leaf"))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks profile other functions and compare the counts with the arithmetic, make sure the built-ins stay out of the counts and the hot spots, measure the peak of a function that allocates and then frees, and run the doubling test on a linear, a quadratic and a halving loop.
skills: [cprofile, tracemalloc, decide]
''',
)
write("exercises/build-a-profiling-toolkit/starter.py", "")
write("exercises/build-a-profiling-toolkit/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-a-profiling-toolkit/test_exercise.py",
    f'''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the four lines."""
    assert run() == {BUILD_OUT!r}


def test_counts_and_hot_spots():
    """Three nested functions have the counts the arithmetic gives; the busiest body is the hot spot; no built-in appears."""
    profile = function("profile")
    call_counts = function("call_counts")
    hot_spots = function("hot_spots")

    def leaf():
        return 1

    def inner():
        total = 0
        for _ in range(4):
            total += leaf()
        return total

    def outer():
        return inner() + inner() + inner()

    def busy():
        total = 0
        for i in range(60_000):
            total += i
        return total

    def both():
        outer()
        return busy()

    _, stats = profile(both)
    counts = call_counts(stats)
    assert counts["leaf"] == 12 and counts["inner"] == 3 and counts["outer"] == 1 and counts["both"] == 1
    assert not any(name.startswith("<method") or name.startswith("<built-in") for name in counts)
    assert hot_spots(stats, 1) == ["busy"] and not any(name.startswith("<method") or name.startswith("<built-in") for name in hot_spots(stats, 20))


def test_peak_bytes():
    """A function that builds and then drops a list of 20,000 floats peaks above 20,000 times 8 bytes, far above its final footprint."""
    peak_bytes = function("peak_bytes")

    def build_and_drop():
        numbers = [float(i) for i in range(20_000)]
        return len(numbers)

    peak = peak_bytes(build_and_drop)
    assert 20_000 * 8 < peak < 20_000 * 200


def test_growth():
    """A linear loop doubles its calls, a quadratic one quadruples them, a logarithmic one barely changes."""
    growth = function("growth")

    def mark():
        return 1

    def linear(n):
        for _ in range(n):
            mark()

    def quadratic(n):
        for _ in range(n):
            for _ in range(n):
                mark()

    def halving(n):
        while n > 1:
            n //= 2
            mark()

    assert growth(linear, lambda n: n, 300, "mark") == 2.0
    assert growth(quadratic, lambda n: n, 30, "mark") == 4.0
    assert growth(halving, lambda n: n, 1024, "mark") == 11 / 10
''',
)
write("exercises/build-a-profiling-toolkit/wrong/counts-the-builtins.py", BUILD_WITH_BUILTINS)
write("exercises/build-a-profiling-toolkit/wrong/by-cumulative-time.py", BUILD_BY_CUMULATIVE)
write("exercises/build-a-profiling-toolkit/wrong/current-not-peak.py", BUILD_CURRENT_NOT_PEAK)
write("exercises/build-a-profiling-toolkit/wrong/never-doubles.py", BUILD_NO_DOUBLING)
write(
    "exercises/build-a-profiling-toolkit/wrong/typed-in.py",
    "def profile(function, *args):\n    return function(*args), None\n\n\ndef call_counts(stats):\n    return {'leaf': 2000, 'branch': 2, 'root': 1}\n\n\ndef hot_spots(stats, k):\n    return ['grind']\n\n\ndef peak_bytes(function, *args):\n    return 10**9\n\n\ndef growth(function, make_input, n, name):\n    return 2.0\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-profile-that-lied/exercise.yaml",
    f'''id: debug-a-profile-that-lied
stage: debug
rev: 1
title: "A profile that lied"
prompt: |
  The program profiles `run`, which calls `light` a thousand times and `heavy` once, and should name the function with the most own time and the number of calls to `light`:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: it crashes with `IndexError`, because the profiler is **disabled before** `run()` is called, so the table has no Python-level rows at all; the work has to happen between `enable` and `disable`. Fix that, and it names `light` as the hot spot: the rows are sorted by **calls** (the second value) when the question is about **own time** (the third). A thousand cheap calls are not a hot spot; one call that does 200,000 iterations is.
skills: [cprofile, decide]
''',
)
write("exercises/debug-a-profile-that-lied/starter.py", DEBUG_STARTER)
write("exercises/debug-a-profile-that-lied/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-profile-that-lied/test_exercise.py",
    f'''import cProfile
import pstats

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Names heavy as the hot spot and counts a thousand calls to light."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_functions_profile_as_described():
    """Under a fresh profile, run calls light a thousand times and heavy once, and heavy holds the most own time."""
    run_it = function("run")
    profiler = cProfile.Profile()
    profiler.enable()
    run_it()
    profiler.disable()
    rows = {{func: row for (file, line, func), row in pstats.Stats(profiler).stats.items()}}
    assert rows["light"][1] == 1000 and rows["heavy"][1] == 1 and rows["heavy"][2] > rows["light"][2]
''',
)
write("exercises/debug-a-profile-that-lied/wrong/still-disabled-early.py", DEBUG_STILL_EARLY)
write("exercises/debug-a-profile-that-lied/wrong/still-by-calls.py", DEBUG_STILL_CALLS)
write(
    "exercises/debug-a-profile-that-lied/wrong/typed-in.py",
    "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-calls-to-from-memory/exercise.yaml",
    f'''id: review-calls-to-from-memory
stage: review_code
rev: 1
title: "A call count, from memory"
prompt: |
  Profile a run of `work(250)`, where `work(n)` calls `step(i)` for each `i` below `n`, with `cProfile.Profile` and `pstats.Stats`, and write `calls_to(stats, name)`, the number of times the function called `name` ran, 0 if never. Print the counts for `step`, `work` and `never`:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [cprofile]
''',
)
write("exercises/review-calls-to-from-memory/starter.py", "")
write("exercises/review-calls-to-from-memory/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-calls-to-from-memory/test_exercise.py",
    f'''import cProfile
import pstats

from checks import function, run


def test_the_output():
    """Prints the three counts."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_another_profile():
    """Counts 7 calls, 1 call and 0 calls in a fresh profile."""
    calls_to = function("calls_to")

    def seven():
        return 1

    def once():
        return sum(seven() for _ in range(7))

    profiler = cProfile.Profile()
    profiler.enable()
    once()
    profiler.disable()
    stats = pstats.Stats(profiler)
    assert calls_to(stats, "seven") == 7 and calls_to(stats, "once") == 1 and calls_to(stats, "never") == 0
''',
)
write("exercises/review-calls-to-from-memory/wrong/returns-a-time.py", FILL_WRONG)
write(
    "exercises/review-calls-to-from-memory/wrong/typed-in.py",
    "def calls_to(stats, name):\n    return 250\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.hw.profiling written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
