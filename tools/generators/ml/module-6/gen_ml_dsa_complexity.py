"""Writes the topic ml.dsa.complexity (Module 6's first topic). Run from the
repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in. The
hidden tests count comparisons instead of timing them, so both runtimes agree.
Files are written as bytes with LF endings."""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.dsa.complexity")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str) -> str:
    result = subprocess.run([sys.executable, "-c", program], capture_output=True, text=True, check=True)
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

EXAMPLE = '''import time


def has_duplicate_slow(items, counter):
    """Compare every pair of items: a loop inside a loop."""
    n = len(items)
    for i in range(n):
        for j in range(i + 1, n):
            counter[0] += 1
            if items[i] == items[j]:
                return True
    return False


def has_duplicate_fast(items, counter):
    """One pass, remembering what has been seen in a set."""
    seen = set()
    for item in items:
        counter[0] += 1
        if item in seen:
            return True
        seen.add(item)
    return False


def steps(function, items):
    counter = [0]
    function(items, counter)
    return counter[0]


def seconds(function, items, repeats):
    """The best of two timings, each of `repeats` runs, per run: many runs of a fast function give the clock something to measure."""
    best = float("inf")
    for _ in range(2):
        start = time.perf_counter()
        for _ in range(repeats):
            function(items, [0])
        best = min(best, (time.perf_counter() - start) / repeats)
    return best


for n in (500, 1000, 2000):
    items = list(range(n))
    print(n, "slow", steps(has_duplicate_slow, items), "fast", steps(has_duplicate_fast, items))

slow_ratio = steps(has_duplicate_slow, list(range(2000))) / steps(has_duplicate_slow, list(range(1000)))
print("steps from 1000 to 2000: slow x", round(slow_ratio, 2), "fast x", round(2000 / 1000, 2))

slow_800 = seconds(has_duplicate_slow, list(range(800)), 1)
slow_1600 = seconds(has_duplicate_slow, list(range(1600)), 1)
fast_1600 = seconds(has_duplicate_fast, list(range(1600)), 50)
print("time from 800 to 1600: slow x", round(slow_1600 / max(slow_800, 1e-9), 1))
print("at 1600, slow takes", round(slow_1600 / max(fast_1600, 1e-9)), "times longer than fast")
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert EX[:4] == [
    "500 slow 124750 fast 500",
    "1000 slow 499500 fast 1000",
    "2000 slow 1999000 fast 2000",
    "steps from 1000 to 2000: slow x 4.0 fast x 2.0",
], EX
TIME_RATIO = float(re.search(r"slow x ([\d.]+)", EX[4]).group(1))
TIMES_SLOWER = int(re.search(r"takes (\d+) times", EX[5]).group(1))
assert 2.5 <= TIME_RATIO <= 6.5 and TIMES_SLOWER >= 20, EX[4:]
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_PAIRS = '''def pairs(n):
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            count += 1
    return count


print(pairs(10), pairs(20), pairs(40))
print(round(pairs(40) / pairs(20), 2))
'''
PREDICT_PAIRS_OUT = out(PREDICT_PAIRS)
assert PREDICT_PAIRS_OUT == "45 190 780\n4.11\n", PREDICT_PAIRS_OUT

REVIEW_HALVING = '''def halvings(n):
    steps = 0
    while n > 1:
        n = n // 2
        steps += 1
    return steps


print(halvings(16), halvings(1024), halvings(1_000_000))
'''
REVIEW_HALVING_OUT = out(REVIEW_HALVING)
assert REVIEW_HALVING_OUT == "4 10 19\n", REVIEW_HALVING_OUT

REVIEW_DOUBLING = '''def steps(n):
    return 3 * n * n + 100 * n


for n in (10, 100, 1000):
    print(n, steps(n), round(steps(2 * n) / steps(n), 2))
'''
REVIEW_DOUBLING_OUT = out(REVIEW_DOUBLING)
assert REVIEW_DOUBLING_OUT == "10 1300 2.46\n100 40000 3.5\n1000 3100000 3.94\n", REVIEW_DOUBLING_OUT

PARSONS_LINES = [
    "count = 0",
    "n = 20",
    "for i in range(n):",
    "    for j in range(i + 1, n):",
    "        count += 1",
    "print(count)",
]
assert out("\n".join(PARSONS_LINES) + "\n") == "190\n"
assert out("\n".join(PARSONS_LINES).replace("range(i + 1, n)", "range(n)") + "\n") == "400\n"

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''def count_steps(n):
    """How many comparisons a nested-loop duplicate check makes on n distinct items."""
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            count += 1
    return count


print(count_steps(10), count_steps(100), count_steps(1000))
print(count_steps(2000) // count_steps(1000))
'''
FILL_STARTER = FILL_SOLUTION.replace("range(i + 1, n)", "range(..., n)").replace("count += 1", "count += ...")
FILL_WRONG = FILL_SOLUTION.replace("range(i + 1, n)", "range(i, n)")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "45 4950 499500\n4\n", FILL_OUT
assert out(FILL_WRONG) != FILL_OUT

# --- the write ----------------------------------------------------------------------------------

WRITE_STARTER = ""
WRITE_SOLUTION = '''def growth_name(counts):
    """Name the growth from step counts at n, 2n, 4n, ...: the average ratio between neighbours."""
    ratios = [later / earlier for earlier, later in zip(counts, counts[1:])]
    average = sum(ratios) / len(ratios)
    if average < 1.5:
        return "constant"
    if average < 3:
        return "linear"
    if average < 6:
        return "quadratic"
    return "faster than quadratic"


print(growth_name([7, 7, 7]))
print(growth_name([100, 201, 398]))
print(growth_name([45, 190, 780]))
print(growth_name([8, 64, 512]))
'''
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "constant\nlinear\nquadratic\nfaster than quadratic\n", WRITE_OUT
WRITE_WRONG = WRITE_SOLUTION.replace("if average < 3:", "if average < 1.9:")
assert out(WRITE_WRONG) != WRITE_OUT

# --- the build ----------------------------------------------------------------------------------

BUILD_SOLUTION = '''def pairs(n):
    """How many pairs a nested loop over n items compares: n * (n - 1) / 2."""
    return n * (n - 1) // 2


def has_duplicate(items):
    """Does any value appear twice? One pass with a set."""
    seen = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False


def common_count(a, b):
    """How many distinct values appear in both lists."""
    in_a = set(a)
    return len({item for item in b if item in in_a})


def growth_name(counts):
    """Name the growth from step counts at n, 2n, 4n, ...: the average ratio between neighbours."""
    ratios = [later / earlier for earlier, later in zip(counts, counts[1:])]
    average = sum(ratios) / len(ratios)
    if average < 1.5:
        return "constant"
    if average < 3:
        return "linear"
    if average < 6:
        return "quadratic"
    return "faster than quadratic"


print(pairs(10), pairs(1000))
print(has_duplicate([3, 1, 4, 1, 5]), has_duplicate(list(range(10000))))
print(common_count(["a", "b", "c"], ["b", "c", "d"]), common_count(list(range(5000)), list(range(2500, 7500))))
print(growth_name([pairs(100), pairs(200), pairs(400)]), growth_name([100, 200, 400]))
'''
BUILD_OUT = out(BUILD_SOLUTION)
assert BUILD_OUT == "45 499500\nTrue False\n2 2500\nquadratic linear\n", BUILD_OUT
BUILD_NESTED = BUILD_SOLUTION.replace(
    '''    seen = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False''',
    '''    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return True
    return False''',
)
BUILD_COMMON_NESTED = BUILD_SOLUTION.replace(
    "    in_a = set(a)\n    return len({item for item in b if item in in_a})",
    "    return len({item for item in b if item in a})",
)
BUILD_PAIRS_OFF = BUILD_SOLUTION.replace("return n * (n - 1) // 2", "return n * n // 2")
assert out(BUILD_NESTED) == BUILD_OUT and out(BUILD_COMMON_NESTED) == BUILD_OUT and out(BUILD_PAIRS_OFF) != BUILD_OUT

TRACKED = '''

class Tracked:
    """A value that counts how often it is compared. Hashing is free; == and < are counted."""

    compared = 0

    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        Tracked.compared += 1
        return self.value == other.value

    def __lt__(self, other):
        Tracked.compared += 1
        return self.value < other.value


def tracked(values):
    return [Tracked(v) for v in values]
'''

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''def unique_in_order(emails):
    """The distinct emails, in the order they first appear."""
    seen = set()
    result = []
    for email in emails:
        if email not in seen:
            seen.add(email)
            result.append(email)
    return result


emails = [f"user{i % 1500}@example.com" for i in range(3000)]
unique = unique_in_order(emails)
print(len(unique), unique[:2], unique[-1])
'''
BUG_LIST = ("    seen = set()", "    seen = []")
BUG_ADD = ("            seen.add(email)", "            seen.append(email)")
BUG_INSERT = ("            result.append(email)", "            result.insert(0, email)")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_LIST).replace(*BUG_ADD).replace(*BUG_INSERT)
DEBUG_STILL_LIST = DEBUG_SOLUTION.replace(*BUG_LIST).replace(*BUG_ADD)
DEBUG_STILL_REVERSED = DEBUG_SOLUTION.replace(*BUG_INSERT)
DEBUG_OUT = out(DEBUG_SOLUTION)
DEBUG_STARTER_OUT = out(DEBUG_STARTER)
print("debug:\n" + DEBUG_OUT + "buggy:\n" + DEBUG_STARTER_OUT)
assert DEBUG_OUT == "1500 ['user0@example.com', 'user1@example.com'] user1499@example.com\n", DEBUG_OUT
assert DEBUG_STARTER_OUT == "1500 ['user1499@example.com', 'user1498@example.com'] user0@example.com\n", DEBUG_STARTER_OUT
assert out(DEBUG_STILL_LIST) == DEBUG_OUT and out(DEBUG_STILL_REVERSED) != DEBUG_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.dsa.complexity
kind: topic
status: ready
title: "Counting steps and big-O"
summary: "How running time grows with the input: counting a function's operations, timing it as its input doubles, the common orders from constant to quadratic, and what a NumPy constant factor does and doesn't change."
prerequisites: [ml.m2.checkpoint]
estimated_minutes: 50
rev: 1
objectives:
  - "Count the operations a function performs as a function of its input size, and name the order: O(1), O(log n), O(n), O(n log n), O(n²)."
  - "Time a function as its input doubles, and read the growth off the timings."
  - "Predict which of two approaches scales, and say when the slower order is fine."
  - "Say what a NumPy vectorized operation changes (the constant) and what it doesn't (the order)."
# Linked, never copied or embedded: the Runestone book is CC BY-NC-SA 4.0;
# Open Data Structures is CC BY 2.5; the Python documentation is under the
# PSF licence.
resources:
  - title: "Problem Solving with Algorithms and Data Structures using Python (Brad Miller and David Ranum), chapter 3: Analysis, sections 3.2 to 3.4 (what analysis is, big-O notation, an anagram detection example)"
    url: https://runestone.academy/ns/books/published/pythonds3/Analysis/toctree.html
    type: reading
    use: link
    license: CC BY-NC-SA 4.0
  - title: "Open Data Structures in Python (Pat Morin), section 1.3: Mathematical Background, the part on big-O notation"
    url: https://opendatastructures.org/ods-python/1_3_Mathematical_Background.html
    type: reading
    use: link
    license: CC BY 2.5
  - title: "The Python documentation: time.perf_counter, the clock for measuring short durations"
    url: https://docs.python.org/3/library/time.html#time.perf_counter
    type: reading
    use: link
    license: "PSF licence (linked, not copied)"
practice:
  - example-doubling-the-input
  - parsons-count-the-nested-loop
  - predict-count-the-pairs
  - mcq-which-is-quadratic
  - mcq-four-times-longer
  - mcq-numpy-and-the-loop
  - mcq-worth-rewriting
  - fill-count-the-steps
  - write-name-the-growth
prove:
  build: build-fast-or-slow
  debug: debug-slow-deduplicate
  explain:
    prompt: |
      A teammate's data-cleaning script took a second on a 5,000-row sample and has now been running for an hour on the full 500,000 rows. They say "it's only a hundred times more data". In your own words: what does it mean to say a piece of code is O(n²), and why would that explain the hour? How would you find a function's order of growth by experiment, without reading its code? Why can a NumPy version of a loop be a hundred times faster and still have the same order, and when does that distinction decide what you should change? And when is the slow order perfectly fine to leave alone?
    rubric:
      - id: count
        required: true
        description: "O(n²) means the number of steps grows like the square of the input size once n is large (constants and smaller terms dropped); a hundred times more rows is ten thousand times more work for a nested loop over pairs, so a second becomes hours."
      - id: doubling
        required: true
        description: "Double the input and measure (counting steps, or timing the best of a few runs): constant stays the same, linear doubles, n log n a bit more than doubles, quadratic quadruples; repeat the doubling to confirm."
      - id: constants
        required: true
        description: "Big-O drops the constant in front: a Python loop and a vectorized NumPy call can both be one pass (order n) with a hundredfold difference in the cost of each step. Vectorizing shrinks the constant; a different algorithm changes the order, and once n is large only the order rescues you."
      - id: choose
        required: true
        description: "At small n or for a job that runs rarely, a quadratic version that finishes in a tenth of a second is fine; the order matters when the data or the frequency grows, which is the question to ask before rewriting."
    model_answer: |
      Saying code is O(n²) means that the number of basic steps it takes grows like the square of the input size, once the input is large enough that the smaller terms and the constant in front stop mattering. The usual cause is a loop inside a loop over the same data, which looks at every pair. That explains the hour: a hundred times more rows is a hundred squared, ten thousand times more pairs, so one second becomes about ten thousand seconds, nearly three hours. To find the order by experiment I would double the input and measure, counting steps if I can instrument the code, or timing the best of a few runs if I can't, and then double again. If the measurement stays the same the function is constant time; if it doubles, linear; if it a bit more than doubles, n log n; if it quadruples, quadratic. The ratio is what to read, not the milliseconds, which depend on the machine. A NumPy version of the same loop can be a hundred times faster and still be the same order because big-O drops the constant: both make one pass over the data, but NumPy's step runs in compiled code and the Python step runs in the interpreter. Vectorizing shrinks the constant; changing the algorithm, say a set instead of a nested loop, changes the order. If the data is going to keep growing, only the change of order keeps the job finishing, and vectorizing a quadratic loop just postpones the hour. And the slow order is fine to leave alone when n is small or the job runs rarely: a nested loop over two hundred records once a night costs a tenth of a second, and rewriting it costs time and risk. The order of growth says what happens when the input grows; it doesn't say the input will.
review_pool:
  - review-predict-halving-steps
  - review-predict-doubling-counts
  - review-mcq-which-finishes
  - review-mcq-same-order-different-speed
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: count
    description: "Count a function's operations as a function of its input size, and name the order of growth"
  - id: doubling
    description: "Find the order of growth by experiment: double the input, measure, and read the ratio"
  - id: choose
    description: "Predict which of two approaches scales, and say when the slower order is fine"
  - id: constants
    description: "Say what vectorizing with NumPy changes (the constant) and what it doesn't (the order)"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

Module 2 taught you to write Python; this module teaches you what it costs. The cost of a function is not seconds but **steps**: how many basic operations it does, and above all how that number grows as the input grows. This topic is that one idea, **order of growth**, written as **big-O**, found two ways: by counting the steps, and by doubling the input and watching. The worked example asks "does this list contain a duplicate?" twice, with a loop inside a loop and with a set, and counts and times both.

The main resource is **_Problem Solving with Algorithms and Data Structures using Python_, chapter 3** (sections 3.2 to 3.4: what analysis is, big-O notation, and an anagram example solved four ways); about 30 minutes, with runnable code. Open Data Structures section 1.3 has the same definitions more tersely. Watch for:

- **Steps, not seconds:** the count is the thing that doesn't depend on the machine.
- **The doubling test:** double the input and see what the cost does.
- **The anagram example:** four programs, four orders, for one question.

</Intro>

<Resource index={{0}} />

<Recap>

- **Count steps, not seconds.** A function's cost is how many basic steps it takes (a comparison, an addition, a lookup) as a function of its input size `n`. Seconds depend on the machine and on what else is running; the count doesn't. The worked example counts the comparisons a nested loop makes to check 500, 1,000 and 2,000 items for a duplicate: 124,750, then 499,500, then 1,999,000, four times more at each doubling. The set version makes 500, 1,000 and 2,000 steps: twice more at each doubling.
- **Order of growth, written as big-O.** `O(n²)`, read "order n squared", means the step count grows like `n²` once `n` is large: `3n² + 10n + 5` is `O(n²)`, because the `n²` term swamps the others and the 3 in front is dropped on purpose. The orders you'll meet, slowest-growing first: `O(1)`, **constant**, the same cost whatever the size (a list index, a dict or set lookup); `O(log n)`, **logarithmic**, growing by one step each time `n` doubles (`log n` is how many times you can halve `n` before one is left: 20 for a million); `O(n)`, **linear**, one pass (`sum`, `max`, `x in a_list`); `O(n log n)`, what sorting costs; `O(n²)`, **quadratic**, a loop inside a loop over the same data.
- **The doubling test** finds the order by experiment. Double `n` and measure again: constant stays the same, linear doubles, `n log n` a little more than doubles, quadratic quadruples. Counting steps gives exact ratios (4.0 for the nested loop, 2.0 for the set); timing gives noisy ones (about 4), so time the best of a few runs and read the ratio, never the milliseconds. In the example the nested loop is a few hundred times slower than the set at 1,600 items, and the gap doubles every time the data does.
- **Constants matter, separately.** Big-O drops the constant in front, so two `O(n)` programs can differ a hundredfold: a Python loop and `np.sum` are both one pass over the data, but NumPy's step runs in compiled code. **Vectorizing** (replacing a Python loop with one NumPy operation) changes the constant; changing the algorithm changes the order. The constant wins at today's size; the order wins once `n` grows, and only the order keeps a job finishing.
- **Worst, best and average.** `x in a_list` stops when it finds `x`: one step at best, `n` at worst, about `n / 2` for a value that's there. Big-O usually names the worst case. A dict or set lookup is `O(1)` **on average** (the next topic says why, and when it isn't).
- **When the slow order is fine:** at small `n`, or for a job that runs rarely. A nested loop over 200 records once a night costs a tenth of a second and isn't worth rewriting. Order is about growth, not about speed today, so the question before a rewrite is "will `n` grow, or will this run often?".
- **In machine learning:** the loop over every pair is the thing that "worked on the sample" and never finishes on the dataset (a hundred times the rows is ten thousand times the pairs); feature code is written once and run on millions of rows; and knowing the order tells you which fix to reach for when the data grows: vectorize, if the constant is the problem, or change the method, if the order is.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-count-the-nested-loop.yaml",
    "id: parsons-count-the-nested-loop\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to count how many pairs a nested loop compares among 20 items, and print `190`. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("    for j in range(n):")
    + "\nexplanation: |\n"
    + block("The inner loop starts at `i + 1`, so each pair is counted once: 19 + 18 + ... + 1 = 190, which is `20 * 19 / 2`. The decoy's inner loop starts at 0 and counts every ordered pair including each item with itself, 400. Both are quadratic; the honest count is half the square.")
    + "skills: [count]\n",
)

write(
    "recall/predict-count-the-pairs.yaml",
    f'''id: predict-count-the-pairs
type: predict_output
rev: 1
prompt: |
  A counter inside a nested loop. What does the program print?
code: |
{block(PREDICT_PAIRS)}expected_output: |
{block(PREDICT_PAIRS_OUT)}explanation: |
  `pairs(n)` is `n * (n - 1) / 2`: 45, 190 and 780. Doubling `n` from 20 to 40 multiplies the count by 4.11, close to the 4 that `n²` predicts; the gap is the `- n` term, which matters less as `n` grows.
skills: [count]
''',
)

mcq(
    "mcq-which-is-quadratic",
    "Four pieces of code run on a list of `n` numbers. Which one does work that grows like `n²`?",
    [
        "`total = sum(items)`, because it touches every number",
        "`for x in items: for y in items: if x + y == 10: ...`",
        "`items.sort()`, because sorting has to compare everything with everything",
        "`10 in a_set`, because a set has to be searched from the start",
    ],
    1,
    "The nested loop runs the inner loop `n` times for each of the `n` outer values: `n²` additions. `sum` makes one pass, `n` steps; Python's `sort` takes about `n log n` comparisons, not `n²`; a set lookup takes a constant number of steps however large the set.",
    ["count"],
)

mcq(
    "mcq-four-times-longer",
    "You double a function's input and it takes about four times as long. You double it again, and again it takes four times as long. What is its order of growth?",
    [
        "Linear: the time goes up every time the input does",
        "Constant: four is a small number",
        "Quadratic: doubling `n` squares to four times the work",
        "Logarithmic: each doubling adds the same amount of time",
    ],
    2,
    "Work that grows like `n²` goes up by `2² = 4` when `n` doubles, every time. Linear work would double; constant work wouldn't change; logarithmic work would gain the same small amount per doubling, not multiply by four.",
    ["doubling"],
)

mcq(
    "mcq-numpy-and-the-loop",
    "Summing a million numbers takes 80 milliseconds in a Python loop and 1 millisecond with `np.sum`. Both are given an array twice as long. What happens?",
    [
        "Both take about twice as long: same order, NumPy's constant is 80 times smaller",
        "NumPy's time stays at about 1 millisecond, because vectorized code runs in constant time",
        "The loop takes four times as long, because Python loops are quadratic in the data",
        "NumPy's time doubles but the loop's quadruples, which is why the gap keeps growing",
    ],
    0,
    "Both are one pass over the data, order `n`: double the data, double the time. What NumPy changes is the constant: each step runs in compiled code instead of the interpreter, about 80 times cheaper here. Big-O drops that constant, which is why \"same order\" and \"same speed\" are different claims.",
    ["constants"],
)

mcq(
    "mcq-worth-rewriting",
    "A nightly script compares every pair of 200 records and takes a tenth of a second. A teammate wants to rewrite it with a set \"because nested loops are quadratic\". Is it worth it?",
    [
        "Yes: a quadratic algorithm is always wrong and should never ship",
        "Yes: a set lookup is constant time, so the script would become instant and stay that way",
        "No: sets only work for numbers, and the records are not numbers",
        "Not yet: at 200 records it is fast enough; rewrite when the count grows",
    ],
    3,
    "Order of growth says what happens as `n` grows, not whether `n` is large. At 200 records a tenth of a second once a night costs nothing, and the rewrite costs time and risk. The order matters the moment the records become 20,000 (a hundred times more records, ten thousand times more pairs) or the script runs on every request.",
    ["choose"],
)

write(
    "recall/review-predict-halving-steps.yaml",
    f'''id: review-predict-halving-steps
type: predict_output
rev: 1
prompt: |
  How many times can you halve a number before it reaches 1? That count is `log2 n`, the cost of a binary search. What does the program print?
code: |
{block(REVIEW_HALVING)}expected_output: |
{block(REVIEW_HALVING_OUT)}explanation: |
  16 halves to 8, 4, 2, 1: four steps. 1,024 is `2` to the 10, so ten. A million isn't a power of two; integer halving reaches 1 after 19 steps (`2` to the 19 is 524,288, `2` to the 20 is over a million). Logarithmic cost grows by one step each time `n` doubles.
skills: [count]
''',
)

write(
    "recall/review-predict-doubling-counts.yaml",
    f'''id: review-predict-doubling-counts
type: predict_output
rev: 1
prompt: |
  A function's step count is `3n² + 100n`. The program prints the count at three sizes and the ratio when `n` doubles. What does it print?
code: |
{block(REVIEW_DOUBLING)}expected_output: |
{block(REVIEW_DOUBLING_OUT)}explanation: |
  At `n = 10` the linear term dominates (1,000 of the 1,300), so doubling only multiplies by 2.46. By `n = 1000` the `n²` term is 30 times the other, and the ratio is 3.94, nearly the 4 of pure `n²`. That is what big-O means by dropping the smaller terms: they fade as `n` grows, and the ratio tends to the order's own.
skills: [doubling]
''',
)

mcq(
    "review-mcq-which-finishes",
    "Two versions of a job both finish in a second on 10,000 rows: A loops over every pair of rows, B makes one pass with a dict. The data is about to grow to 10 million rows. What happens?",
    [
        "Both take about a thousand times longer, since the data is a thousand times bigger and that is all that changes",
        "B takes about a thousand times longer; A about a million times longer",
        "A takes a thousand times longer; B takes a million, because dicts fill up",
        "Neither finishes; 10 million rows needs a database whatever the algorithm",
    ],
    1,
    "A thousand times the rows is a thousand times the work for a linear pass (about 17 minutes) and a thousand squared, a million times, for every pair (about 12 days). The dict doesn't fill up: its lookups stay constant time on average. Big-O is the tool for exactly this question, what happens when the data grows.",
    ["choose"],
)

mcq(
    "review-mcq-same-order-different-speed",
    "Two functions are both order `n`. Can one be 100 times slower than the other on every input?",
    [
        "No: the same order of growth means the same running time",
        "Only for small inputs; for large ones the order takes over and they match",
        "Yes: big-O keeps the shape of the growth and drops the constant",
        "Yes, but only if one of them is secretly `n log n`",
    ],
    2,
    "Order `n` says the time doubles when the input doubles; it says nothing about the constant, which depends on what each step costs. A Python loop and a NumPy call can both be order `n` with a constant that differs a hundredfold, at every size. That is the difference between an algorithm's order and a program's speed.",
    ["constants"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-doubling-the-input/exercise.yaml",
    f'''id: example-doubling-the-input
stage: worked_example
rev: 1
title: "Doubling the input"
prompt: |
  Two ways to ask "does this list contain a duplicate?", counted and timed as the list doubles. Press **Run**, then read how each part works. The last two lines are timings, so your numbers will differ a little from the notes; the ratios are what to read.
steps:
  - label: "Two ways to ask the same question"
    lines: "{ln('def has_duplicate_slow')}-{ln('    return False', ln('def has_duplicate_fast'))}"
    note: "The slow way compares every pair: for each item, a loop over the items after it. The fast way makes one pass and remembers what it has seen in a set, where `item in seen` is a constant-time lookup. Both take a `counter`, a one-element list they add to, so the caller can count their steps."
  - label: "Counting steps"
    lines: "{ln('def steps')}-{ln('    return counter[0]')}"
    note: "A list is used as the counter because the function can change what's inside it (Module 2's references). Each function adds one for every comparison it makes, and `steps` reads the total."
  - label: "Timing, carefully"
    lines: "{ln('def seconds')}-{ln('    return best')}"
    note: "`time.perf_counter()` is a clock fine enough for milliseconds, but not always finer: the fast function runs 50 times in a batch so there is something to measure. A single timing is noisy (other programs, the first run warming up), so each batch runs twice and the best is kept."
  - label: "The counts"
    lines: "{ln('for n in (500, 1000, 2000)')}-{ln('    print(n, ')}"
    note: "With no duplicate present, the slow way compares every pair: 124,750 comparisons for 500 items, 499,500 for 1,000, 1,999,000 for 2,000, four times more at each doubling, because the number of pairs is about `n² / 2`. The fast way makes one step per item: 500, 1,000, 2,000."
  - label: "Doubling, in steps"
    lines: "{ln('slow_ratio =')}-{ln('steps from 1000 to 2000')}"
    note: "The ratio of the counts at 2,000 and 1,000 items: 4.0 for the nested loop, 2.0 for the set. Exact, because counts don't depend on the machine. That is the doubling test: quadruples means quadratic, doubles means linear."
  - label: "Doubling, in time"
    lines: "{ln('slow_800 =')}-{ln('times longer than fast')}"
    note: "The same test with a clock: the nested loop at 1,600 items against 800 took about {TIME_RATIO:.0f} times as long when this was written (yours will be near 4, give or take the noise), and at 1,600 items the set version was about {TIMES_SLOWER} times faster. Ratios are what to read, never the milliseconds, and the gap doubles each time the data does."
''',
)
write("exercises/example-doubling-the-input/solution.py", EXAMPLE)
write(
    "exercises/example-doubling-the-input/test_exercise.py",
    f'''import re

from checks import run


def test_the_walkthrough():
    """Prints the exact step counts, then two timing lines whose numbers depend on the machine and are not checked."""
    lines = run().splitlines()
    assert lines[:4] == {EX[:4]!r}, lines
    assert re.fullmatch(r"time from 800 to 1600: slow x [\\d.]+", lines[4]), lines[4]
    assert re.fullmatch(r"at 1600, slow takes \\d+ times longer than fast", lines[5]), lines[5]
''',
)

write(
    "exercises/fill-count-the-steps/exercise.yaml",
    f'''id: fill-count-the-steps
stage: fill_in
rev: 1
title: "Count the steps"
prompt: |
  `count_steps(n)` should count the comparisons a nested-loop duplicate check makes on `n` distinct items: for each item, one comparison with every item **after** it. Replace each `...` so the program prints the counts for 10, 100 and 1,000 items, and how many times more steps 2,000 items take than 1,000:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "The inner loop should start just after `i`, so each pair is counted once and no item is compared with itself."
  - "Every time the inner loop runs its body, that is one comparison."
skills: [count]
''',
)
write("exercises/fill-count-the-steps/starter.py", FILL_STARTER)
write("exercises/fill-count-the-steps/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-count-the-steps/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the three counts and the doubling ratio."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_small_cases():
    """One item makes no comparisons, two make one, five make ten."""
    count_steps = function("count_steps")
    assert (count_steps(1), count_steps(2), count_steps(5)) == (0, 1, 10)
''',
)
write("exercises/fill-count-the-steps/wrong/starts-at-i.py", FILL_WRONG)
write(
    "exercises/fill-count-the-steps/wrong/typed-in.py",
    "def count_steps(n):\n    return 45\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-name-the-growth/exercise.yaml",
    f'''id: write-name-the-growth
stage: write
rev: 1
title: "Name the growth"
prompt: |
  Write `growth_name(counts)`, which takes a list of step counts measured at sizes `n`, `2n`, `4n` and so on, and names the growth from the **average ratio** between neighbouring counts: below 1.5 is `"constant"`, below 3 is `"linear"`, below 6 is `"quadratic"`, and anything else is `"faster than quadratic"`. (An `n log n` function a bit more than doubles, so this rough test calls it linear; that is a known limit of the doubling test.) Then print it for these four lists:

  ```python
  print(growth_name([7, 7, 7]))
  print(growth_name([100, 201, 398]))
  print(growth_name([45, 190, 780]))
  print(growth_name([8, 64, 512]))
  ```

  ```
{block(WRITE_OUT)}  ```
hints:
  - "`zip(counts, counts[1:])` pairs each count with the next one."
  - "Divide the later count by the earlier one for each pair, then average the ratios."
skills: [doubling]
''',
)
write("exercises/write-name-the-growth/starter.py", WRITE_STARTER)
write("exercises/write-name-the-growth/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-name-the-growth/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the four names."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_the_borders():
    """A near-flat count is constant, an n log n count reads as linear, cubic growth is faster than quadratic."""
    growth_name = function("growth_name")
    assert growth_name([1000, 1000, 1001]) == "constant"
    assert growth_name([10000, 22000, 48000]) == "linear"
    assert growth_name([1, 8, 64]) == "faster than quadratic"
''',
)
write("exercises/write-name-the-growth/wrong/linear-too-narrow.py", WRITE_WRONG)
write(
    "exercises/write-name-the-growth/wrong/typed-in.py",
    "def growth_name(counts):\n    return 'constant'\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-fast-or-slow/exercise.yaml",
    f'''id: build-fast-or-slow
stage: build
rev: 1
title: "Fast or slow"
prompt: |
  Starting from a blank editor, write four functions:

  - `pairs(n)`: how many pairs a nested loop over `n` items compares, `n * (n - 1) / 2`, as an int.
  - `has_duplicate(items)`: whether any value appears twice, in **one pass** (a set), not a loop inside a loop.
  - `common_count(a, b)`: how many distinct values appear in both lists, again without a loop inside a loop.
  - `growth_name(counts)`: the name of the growth from step counts at `n`, `2n`, `4n`, ... by the average ratio between neighbours: below 1.5 `"constant"`, below 3 `"linear"`, below 6 `"quadratic"`, else `"faster than quadratic"`.

  Then print:

  ```python
  print(pairs(10), pairs(1000))
  print(has_duplicate([3, 1, 4, 1, 5]), has_duplicate(list(range(10000))))
  print(common_count(["a", "b", "c"], ["b", "c", "d"]), common_count(list(range(5000)), list(range(2500, 7500))))
  print(growth_name([pairs(100), pairs(200), pairs(400)]), growth_name([100, 200, 400]))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks count how many times your code compares two elements. On 3,000 items, a one-pass `has_duplicate` compares a few thousand times at most; a nested loop compares 4,498,500 times and fails. The same for `common_count`.
skills: [count, doubling, choose]
''',
)
write("exercises/build-fast-or-slow/starter.py", "")
write("exercises/build-fast-or-slow/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-fast-or-slow/test_exercise.py",
    f'''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).
{TRACKED}

def test_the_output():
    """Prints the four lines."""
    assert run() == {BUILD_OUT!r}


def test_pairs():
    """pairs(1) is 0, pairs(2) is 1, pairs(3000) is 4,498,500."""
    pairs = function("pairs")
    assert (pairs(1), pairs(2), pairs(3000)) == (0, 1, 4498500)


def test_has_duplicate_scales():
    """On 3,000 distinct items, has_duplicate compares elements fewer than 60,000 times (a nested loop makes 4,498,500), and still finds a repeat."""
    has_duplicate = function("has_duplicate")
    Tracked.compared = 0
    assert not has_duplicate(tracked(range(3000)))
    assert Tracked.compared < 60_000
    assert has_duplicate(tracked([5, 2, 5]))


def test_common_count_scales():
    """On two lists of 3,000 with 1,000 values in common, common_count is 1,000 after fewer than 120,000 comparisons."""
    common_count = function("common_count")
    Tracked.compared = 0
    assert common_count(tracked(range(3000)), tracked(range(2000, 5000))) == 1000
    assert Tracked.compared < 120_000
    assert common_count(tracked([1, 1, 2]), tracked([1, 1, 1])) == 1


def test_growth_name():
    """A flat count is constant, an n log n count reads as linear, cubic growth is faster than quadratic."""
    growth_name = function("growth_name")
    assert growth_name([1000, 1000, 1001]) == "constant"
    assert growth_name([10000, 22000, 48000]) == "linear"
    assert growth_name([1, 8, 64]) == "faster than quadratic"
''',
)
write("exercises/build-fast-or-slow/wrong/nested-duplicate.py", BUILD_NESTED)
write("exercises/build-fast-or-slow/wrong/nested-common.py", BUILD_COMMON_NESTED)
write("exercises/build-fast-or-slow/wrong/pairs-off.py", BUILD_PAIRS_OFF)
write(
    "exercises/build-fast-or-slow/wrong/typed-in.py",
    "def pairs(n):\n    return 45\n\n\ndef has_duplicate(items):\n    return False\n\n\ndef common_count(a, b):\n    return 2\n\n\ndef growth_name(counts):\n    return 'linear'\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-slow-deduplicate/exercise.yaml",
    f'''id: debug-slow-deduplicate
stage: debug
rev: 1
title: "A slow deduplicate"
prompt: |
  `unique_in_order` should return the distinct emails in the order they first appear, and the program should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the order is backwards, because each new email is inserted at the **front** of the result (and `insert(0, ...)` shifts every element along, a linear step inside the loop). Fix that, and the output is right but the function is quadratic: `seen` is a list, so `email not in seen` scans it from the start every time. The checks count the comparisons: with a set they stay in the thousands, with the list they reach the millions.
skills: [count, choose]
''',
)
write("exercises/debug-slow-deduplicate/starter.py", DEBUG_STARTER)
write("exercises/debug-slow-deduplicate/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-slow-deduplicate/test_exercise.py",
    f'''from checks import function, run

EXPECTED = {DEBUG_OUT!r}
{TRACKED}

def test_the_output():
    """Prints 1500 distinct emails, first appearance first."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_scales():
    """On 3,000 values with 1,500 distinct, the function compares fewer than 30,000 times (a list makes about 2 million) and keeps the first-seen order."""
    unique_in_order = function("unique_in_order")
    values = tracked([i % 1500 for i in range(3000)])
    Tracked.compared = 0
    result = unique_in_order(values)
    assert [item.value for item in result] == list(range(1500)), "the order or the set of values is wrong"
    assert Tracked.compared < 30_000, f"{{Tracked.compared}} comparisons: seen must be a set"
''',
)
write("exercises/debug-slow-deduplicate/wrong/still-list.py", DEBUG_STILL_LIST)
write("exercises/debug-slow-deduplicate/wrong/still-reversed.py", DEBUG_STILL_REVERSED)
write(
    "exercises/debug-slow-deduplicate/wrong/typed-in.py",
    "def unique_in_order(emails):\n    return []\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

print("ml.dsa.complexity written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
