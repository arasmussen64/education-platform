"""Writes the topic ml.dsa.dynamic-programming (Module 6's seventh topic).
Run from the repository root under uv (python -m uv run python <this file>),
so every program's expected output is captured from CPython rather than typed
in. Every count here is a call count or a table entry, so both runtimes agree.
Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.dsa.dynamic-programming")


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

EXAMPLE = '''from functools import lru_cache

calls = 0


def fib_plain(n):
    """The definition as a function: two calls per call, most of them repeats."""
    global calls
    calls += 1
    if n < 2:
        return n
    return fib_plain(n - 1) + fib_plain(n - 2)


print("fib_plain(25) =", fib_plain(25), "after", calls, "calls")

memo = {}


def fib_memo(n):
    """The same, remembering every answer in a dict."""
    global calls
    calls += 1
    if n < 2:
        return n
    if n not in memo:
        memo[n] = fib_memo(n - 1) + fib_memo(n - 2)
    return memo[n]


calls = 0
print("fib_memo(25) =", fib_memo(25), "after", calls, "calls")


@lru_cache(maxsize=None)
def fib_cached(n):
    """The same, with the standard library remembering for you."""
    if n < 2:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)


print("fib_cached(25) =", fib_cached(25), fib_cached.cache_info())


def fib_bottom_up(n):
    """Smallest cases first, keeping only the last two: no recursion at all."""
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


print("fib_bottom_up(90) =", fib_bottom_up(90))


def edit_distance(a, b):
    """The fewest single-character edits (insert, delete, substitute) turning a into b, with the table."""
    table = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        table[i][0] = i
    for j in range(len(b) + 1):
        table[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            table[i][j] = min(table[i - 1][j] + 1, table[i][j - 1] + 1, table[i - 1][j - 1] + cost)
    return table[len(a)][len(b)], table


def edits(a, b, table):
    """Walk the table back from the corner to list the edits that were counted."""
    i, j = len(a), len(b)
    steps = []
    while i > 0 or j > 0:
        cost = 0 if i > 0 and j > 0 and a[i - 1] == b[j - 1] else 1
        if i > 0 and j > 0 and table[i][j] == table[i - 1][j - 1] + cost:
            if cost:
                steps.append(f"substitute {a[i - 1]} with {b[j - 1]}")
            i, j = i - 1, j - 1
        elif i > 0 and table[i][j] == table[i - 1][j] + 1:
            steps.append(f"delete {a[i - 1]}")
            i -= 1
        else:
            steps.append(f"insert {b[j - 1]}")
            j -= 1
    return steps[::-1]


distance, table = edit_distance("kitten", "sitting")
print("kitten -> sitting:", distance, "edits")
for row in table:
    print(" ".join(f"{cell:2}" for cell in row))
print(edits("kitten", "sitting", table))


def knapsack(items, capacity):
    """The most valuable set of items that fits: a table of the best value by items considered and room left."""
    best = [[0] * (capacity + 1) for _ in range(len(items) + 1)]
    for i, (name, weight, value) in enumerate(items, start=1):
        for room in range(capacity + 1):
            best[i][room] = best[i - 1][room]
            if weight <= room:
                best[i][room] = max(best[i][room], best[i - 1][room - weight] + value)
    chosen = []
    room = capacity
    for i in range(len(items), 0, -1):
        if best[i][room] != best[i - 1][room]:
            name, weight, value = items[i - 1]
            chosen.append(name)
            room -= weight
    return best[len(items)][capacity], chosen[::-1]


gear = [("tent", 5, 60), ("stove", 3, 50), ("water", 4, 70), ("book", 2, 30)]
print("knapsack of 9:", knapsack(gear, 9))
greedy, room = [], 9
for name, weight, value in sorted(gear, key=lambda item: -item[2]):
    if weight <= room:
        greedy.append(name)
        room -= weight
print("greedy by value:", greedy, "worth", sum(value for name, weight, value in gear if name in greedy))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert EX[0] == "fib_plain(25) = 75025 after 242785 calls", EX[0]
assert EX[1] == "fib_memo(25) = 75025 after 49 calls", EX[1]
assert EX[2] == "fib_cached(25) = 75025 CacheInfo(hits=23, misses=26, maxsize=None, currsize=26)", EX[2]
assert EX[3] == "fib_bottom_up(90) = 2880067194370816120", EX[3]
assert EX[4] == "kitten -> sitting: 3 edits", EX[4]
assert EX[5] == " 0  1  2  3  4  5  6  7" and EX[11] == " 6  6  5  4  3  3  2  3", EX[5:12]
assert EX[12] == "['substitute k with s', 'substitute e with i', 'insert g']", EX[12]
assert EX[13] == "knapsack of 9: (150, ['stove', 'water', 'book'])", EX[13]
assert EX[14] == "greedy by value: ['water', 'tent'] worth 130", EX[14]
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_CALLS = '''calls = 0


def fib(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


print(fib(10), calls)
calls = 0
memo = {}


def fib_memo(n):
    global calls
    calls += 1
    if n < 2:
        return n
    if n not in memo:
        memo[n] = fib_memo(n - 1) + fib_memo(n - 2)
    return memo[n]


print(fib_memo(10), calls)
'''
PREDICT_CALLS_OUT = out(PREDICT_CALLS)
assert PREDICT_CALLS_OUT == "55 177\n55 19\n", PREDICT_CALLS_OUT

REVIEW_ROW = '''a, b = "ab", "ac"
table = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
for i in range(len(a) + 1):
    table[i][0] = i
for j in range(len(b) + 1):
    table[0][j] = j
for i in range(1, len(a) + 1):
    for j in range(1, len(b) + 1):
        cost = 0 if a[i - 1] == b[j - 1] else 1
        table[i][j] = min(table[i - 1][j] + 1, table[i][j - 1] + 1, table[i - 1][j - 1] + cost)
for row in table:
    print(row)
'''
REVIEW_ROW_OUT = out(REVIEW_ROW)
assert REVIEW_ROW_OUT == "[0, 1, 2]\n[1, 0, 1]\n[2, 1, 1]\n", REVIEW_ROW_OUT

PARSONS_LINES = [
    "memo = {}",
    "def fib(n):",
    "    if n < 2:",
    "        return n",
    "    if n not in memo:",
    "        memo[n] = fib(n - 1) + fib(n - 2)",
    "    return memo[n]",
    "print(fib(50))",
]
assert out("\n".join(PARSONS_LINES) + "\n") == "12586269025\n"

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''memo = {}


def paths(rows, cols):
    """Ways to walk from the top-left of a grid to the bottom-right, moving only right or down."""
    if rows == 0 or cols == 0:
        return 1
    if (rows, cols) not in memo:
        memo[(rows, cols)] = paths(rows - 1, cols) + paths(rows, cols - 1)
    return memo[(rows, cols)]


print(paths(2, 2), paths(10, 10), paths(16, 16))
'''
FILL_STARTER = FILL_SOLUTION.replace("    if (rows, cols) not in memo:", "    if (rows, cols) not in ...:").replace("    return memo[(rows, cols)]", "    return memo[...]")
FILL_WRONG = FILL_SOLUTION.replace("    if rows == 0 or cols == 0:\n        return 1", "    if rows == 0 or cols == 0:\n        return 0")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "6 184756 601080390\n", FILL_OUT
assert out(FILL_WRONG) != FILL_OUT

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''def min_coins(coins, amount):
    """The fewest coins that make the amount, or -1 if none can: a table from 0 up to the amount."""
    best = [0] + [float("inf")] * amount
    for total in range(1, amount + 1):
        for coin in coins:
            if coin <= total and best[total - coin] + 1 < best[total]:
                best[total] = best[total - coin] + 1
    return best[amount] if best[amount] != float("inf") else -1


print(min_coins([1, 5, 10, 25], 63))
print(min_coins([1, 15, 25], 30))
print(min_coins([4, 7], 10))
'''
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "6\n2\n-1\n", WRITE_OUT
WRITE_GREEDY = '''def min_coins(coins, amount):
    count = 0
    for coin in sorted(coins, reverse=True):
        count += amount // coin
        amount %= coin
    return count if amount == 0 else -1


print(min_coins([1, 5, 10, 25], 63))
print(min_coins([1, 15, 25], 30))
print(min_coins([4, 7], 10))
'''
assert out(WRITE_GREEDY) != WRITE_OUT

# --- the build ----------------------------------------------------------------------------------

BUILD_SOLUTION = '''def fib(n):
    """The n-th Fibonacci number, smallest cases first, with no recursion."""
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


def edit_distance(a, b):
    """The fewest single-character inserts, deletes and substitutions turning a into b."""
    table = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        table[i][0] = i
    for j in range(len(b) + 1):
        table[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            table[i][j] = min(table[i - 1][j] + 1, table[i][j - 1] + 1, table[i - 1][j - 1] + cost)
    return table[len(a)][len(b)]


def knapsack(items, capacity):
    """(best value, names chosen in the given order) for items of (name, weight, value) that fit the capacity."""
    best = [[0] * (capacity + 1) for _ in range(len(items) + 1)]
    for i, (name, weight, value) in enumerate(items, start=1):
        for room in range(capacity + 1):
            best[i][room] = best[i - 1][room]
            if weight <= room:
                best[i][room] = max(best[i][room], best[i - 1][room - weight] + value)
    chosen = []
    room = capacity
    for i in range(len(items), 0, -1):
        if best[i][room] != best[i - 1][room]:
            chosen.append(items[i - 1][0])
            room -= items[i - 1][1]
    return best[len(items)][capacity], chosen[::-1]


def min_coins(coins, amount):
    """The fewest coins that make the amount, or -1 if none can."""
    best = [0] + [float("inf")] * amount
    for total in range(1, amount + 1):
        for coin in coins:
            if coin <= total and best[total - coin] + 1 < best[total]:
                best[total] = best[total - coin] + 1
    return best[amount] if best[amount] != float("inf") else -1


print(fib(10), fib(90))
print(edit_distance("kitten", "sitting"), edit_distance("", "abc"), edit_distance("flaw", "lawn"))
gear = [("tent", 5, 60), ("stove", 3, 50), ("water", 4, 70), ("book", 2, 30)]
print(knapsack(gear, 9))
print(min_coins([1, 5, 10, 25], 63), min_coins([1, 15, 25], 30), min_coins([4, 7], 10))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == "55 2880067194370816120\n3 3 2\n(150, ['stove', 'water', 'book'])\n6 2 -1\n", BUILD_OUT
BUILD_NO_MATCH_DISCOUNT = BUILD_SOLUTION.replace("            cost = 0 if a[i - 1] == b[j - 1] else 1\n            table[i][j] = min(table[i - 1][j] + 1, table[i][j - 1] + 1, table[i - 1][j - 1] + cost)\n    return table[len(a)][len(b)]", "            table[i][j] = min(table[i - 1][j] + 1, table[i][j - 1] + 1, table[i - 1][j - 1] + 1)\n    return table[len(a)][len(b)]")
BUILD_GREEDY_KNAPSACK = BUILD_SOLUTION.replace(
    '''    best = [[0] * (capacity + 1) for _ in range(len(items) + 1)]
    for i, (name, weight, value) in enumerate(items, start=1):
        for room in range(capacity + 1):
            best[i][room] = best[i - 1][room]
            if weight <= room:
                best[i][room] = max(best[i][room], best[i - 1][room - weight] + value)
    chosen = []
    room = capacity
    for i in range(len(items), 0, -1):
        if best[i][room] != best[i - 1][room]:
            chosen.append(items[i - 1][0])
            room -= items[i - 1][1]
    return best[len(items)][capacity], chosen[::-1]''',
    '''    chosen, room, total = [], capacity, 0
    for name, weight, value in sorted(items, key=lambda item: -item[2]):
        if weight <= room:
            chosen.append(name)
            room -= weight
            total += value
    return total, [name for name, weight, value in items if name in chosen]''',
)
BUILD_GREEDY_COINS = BUILD_SOLUTION.replace(
    '''    best = [0] + [float("inf")] * amount
    for total in range(1, amount + 1):
        for coin in coins:
            if coin <= total and best[total - coin] + 1 < best[total]:
                best[total] = best[total - coin] + 1
    return best[amount] if best[amount] != float("inf") else -1''',
    '''    count = 0
    for coin in sorted(coins, reverse=True):
        count += amount // coin
        amount %= coin
    return count if amount == 0 else -1''',
)
for wrong in (BUILD_NO_MATCH_DISCOUNT, BUILD_GREEDY_KNAPSACK, BUILD_GREEDY_COINS):
    assert wrong != BUILD_SOLUTION and out(wrong) != BUILD_OUT

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''def edit_distance(a, b):
    """The fewest single-character inserts, deletes and substitutions turning a into b."""
    table = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        table[i][0] = i
    for j in range(len(b) + 1):
        table[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            table[i][j] = min(table[i - 1][j] + 1, table[i][j - 1] + 1, table[i - 1][j - 1] + cost)
    return table[len(a)][len(b)]


for a, b in (("kitten", "sitting"), ("", "abc"), ("flaw", "lawn"), ("same", "same")):
    print(repr(a), "->", repr(b), edit_distance(a, b))
'''
BUG_NO_EDGES = ("    for i in range(len(a) + 1):\n        table[i][0] = i\n    for j in range(len(b) + 1):\n        table[0][j] = j\n", "")
BUG_ALWAYS_COST = ("            cost = 0 if a[i - 1] == b[j - 1] else 1", "            cost = 1")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_NO_EDGES).replace(*BUG_ALWAYS_COST)
DEBUG_STILL_NO_EDGES = DEBUG_SOLUTION.replace(*BUG_NO_EDGES)
DEBUG_STILL_ALWAYS_COST = DEBUG_SOLUTION.replace(*BUG_ALWAYS_COST)
DEBUG_OUT = out(DEBUG_SOLUTION)
STARTER_OUT = out(DEBUG_STARTER)
EDGES_OUT = out(DEBUG_STILL_NO_EDGES)
COST_OUT = out(DEBUG_STILL_ALWAYS_COST)
print("debug:\n" + DEBUG_OUT + "starter:\n" + STARTER_OUT + "edges only:\n" + EDGES_OUT + "cost only:\n" + COST_OUT)
assert DEBUG_OUT == "'kitten' -> 'sitting' 3\n'' -> 'abc' 3\n'flaw' -> 'lawn' 2\n'same' -> 'same' 0\n", DEBUG_OUT
assert STARTER_OUT != DEBUG_OUT and EDGES_OUT != DEBUG_OUT and COST_OUT != DEBUG_OUT
STARTER_LINES = STARTER_OUT.splitlines()
COST_LINES = COST_OUT.splitlines()

REVIEW_CODE_SOLUTION = '''def ways(n):
    """Ways to climb n stairs taking 1 or 2 steps at a time, smallest cases first."""
    one_below, here = 1, 1
    for _ in range(n):
        one_below, here = here, one_below + here
    return one_below


print(ways(1), ways(2), ways(5), ways(30))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "1 2 8 1346269\n", REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.dsa.dynamic-programming
kind: topic
status: ready
title: "Dynamic programming"
summary: "Problems whose answer is built from the answers to smaller versions: memoization with a dict and with lru_cache, tables filled bottom-up, and three classics, Fibonacci, the edit distance between two strings, and the knapsack."
prerequisites: [ml.dsa.stacks-queues-recursion, ml.dsa.arrays-and-hashing]
estimated_minutes: 60
rev: 1
objectives:
  - "Spot overlapping subproblems, and say why plain recursion repeats work exponentially."
  - "Memoize a recursive function with a dict and with functools.lru_cache, and count the calls saved."
  - "Fill a table bottom-up for the edit distance between two strings, and read the edits back out of it."
  - "Solve the knapsack problem with a table, and say what makes a problem a dynamic-programming problem."
# Linked, never copied or embedded: the Runestone book is CC BY-NC-SA 4.0;
# the Python documentation is under the PSF licence; Wikipedia is CC BY-SA 4.0.
resources:
  - title: "Problem Solving with Algorithms and Data Structures using Python (Brad Miller and David Ranum), section 5.12: Dynamic Programming (the coin-change problem, from plain recursion to a table)"
    url: https://runestone.academy/ns/books/published/pythonds3/Recursion/DynamicProgramming.html
    type: reading
    use: link
    license: CC BY-NC-SA 4.0
  - title: "The Python documentation: functools.lru_cache, memoization as a decorator"
    url: https://docs.python.org/3/library/functools.html#functools.lru_cache
    type: reading
    use: link
    license: "PSF licence (linked, not copied)"
  - title: "Wikipedia: Levenshtein distance (the Definition and Example sections)"
    url: https://en.wikipedia.org/wiki/Levenshtein_distance
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
practice:
  - example-fibonacci-edits-and-a-knapsack
  - predict-the-call-counts
  - mcq-why-exponential
  - parsons-a-memo-dict
  - mcq-what-lru-cache-needs
  - mcq-one-cell-of-the-table
  - mcq-what-makes-it-dynamic-programming
  - fill-paths-through-a-grid
  - write-fewest-coins
prove:
  build: build-three-tables
  debug: debug-an-edit-distance
  explain:
    prompt: |
      A teammate's function that scores every way of aligning two gene sequences takes seconds on short ones and never finishes on long ones; another wants to pick the subset of experiments that fits a compute budget and plans to "take the most valuable ones first". In your own words: what overlapping subproblems are and why plain recursion on them is exponential; what memoization is, what lru_cache does and needs, and why a bottom-up table is sometimes better; how the edit-distance table is built and read back; and what makes a problem suitable for dynamic programming rather than for a greedy choice.
    rubric:
      - id: overlap
        required: true
        description: "The recursion reaches the same smaller cases many times (Fibonacci's fib(n-2) is computed twice, its sub-cases four times), so the call tree grows like 2 to the n; the number of distinct subproblems is only n (or n times m)."
      - id: memo
        required: true
        description: "Memoization stores each subproblem's answer the first time (a dict keyed by the arguments, or functools.lru_cache(maxsize=None), whose arguments must be hashable), so each is computed once; bottom-up fills a table from the smallest cases in a loop, avoids the recursion limit, and often keeps only the last row."
      - id: edit-distance
        required: true
        description: "table[i][j] is the distance between the first i characters of one string and the first j of the other: the first row and column count inserts and deletes, each cell is the minimum of delete (up + 1), insert (left + 1) and substitute or match (diagonal + 1 or + 0); the corner is the answer, and walking back along the choices lists the edits."
      - id: knapsack
        required: true
        description: "Dynamic programming needs optimal substructure (the best answer is built from best answers to smaller versions) and overlapping subproblems; greedy by value fails the 0/1 knapsack because taking the most valuable item can block a better combination, and the table over items and capacity finds the best combination."
    model_answer: |
      Overlapping subproblems are what happens when a recursive solution reaches the same smaller case many times. Fibonacci is the simplest example: fib(n) calls fib(n-1) and fib(n-2), fib(n-1) calls fib(n-2) again, and so on down, so the call tree roughly doubles at every level and the work grows like two to the n, even though there are only n different numbers to compute. The alignment function has the same shape: the best alignment of two prefixes is asked for over and over from different branches, so it is exponential in the length of the sequences. Memoization is the fix that keeps the recursion: store each answer the first time it is computed, in a dict keyed by the arguments, and return the stored answer after that, so each subproblem is computed once and the exponential tree collapses to a number of calls proportional to the number of subproblems. functools.lru_cache does that with a decorator; it needs the arguments to be hashable, because they are the dict keys, and maxsize=None so nothing is thrown away. A bottom-up table does the same without recursion: fill the smallest cases first in a loop and build up, which avoids the recursion limit on long inputs and often needs only the previous row, so it uses less memory too. The edit-distance table has a row for each prefix of the first string and a column for each prefix of the second. The first row and column are just lengths, because turning a prefix into nothing takes that many deletes and nothing into a prefix that many inserts. Every other cell is the smallest of three options: the cell above plus one (delete a character), the cell to the left plus one (insert one), or the diagonal cell plus one for a substitution, or plus nothing if the two characters already match. The bottom-right corner is the distance, and walking back from it, choosing at each cell the neighbour that produced it, lists the actual edits. A problem suits dynamic programming when it has optimal substructure, meaning the best answer is built from best answers to smaller versions, and overlapping subproblems, meaning those smaller versions recur. Picking experiments to fit a budget is the knapsack problem, and taking the most valuable ones first is a greedy choice that can fail: the most valuable experiment can use up budget that two cheaper ones would have spent better. The table over experiments and budget considers, for each experiment, both taking it and leaving it, and finds the best combination, which greedy never checks.
review_pool:
  - review-predict-a-small-table
  - review-mcq-top-down-or-bottom-up
  - review-mcq-greedy-fails
  - review-climb-stairs
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: overlap
    description: "Spot overlapping subproblems, and say why plain recursion on them is exponential"
  - id: memo
    description: "Memoize with a dict and with lru_cache, and fill a table bottom-up"
  - id: edit-distance
    description: "Build the edit-distance table and read the edits back out of it"
  - id: knapsack
    description: "Solve the knapsack with a table, and say what makes a problem dynamic programming rather than greedy"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

Some recursive functions are exponential not because the problem is hard but because they solve the same small cases again and again. **Dynamic programming** is the fix: remember each answer, or build the answers up from the smallest case in a table. This topic counts the waste in a plain recursive Fibonacci, removes it three ways, and then builds two tables that every ML engineer meets: the **edit distance** between two strings and the **knapsack**, the best set of things that fits a budget.

The main resource is **_Problem Solving with Algorithms and Data Structures using Python_, section 5.12, Dynamic Programming**, which takes the coin-change problem from plain recursion through memoization to a table; about 25 minutes. The `lru_cache` documentation is the reference for memoizing with a decorator, and Wikipedia's _Levenshtein distance_ has the table. Watch for:

- **The call tree** of the plain recursion, and how little of it is new.
- **The recurrence**: each answer written in terms of smaller answers.
- **The table** as the recurrence filled in from the bottom.

</Intro>

<Resource index={{0}} />

<Recap>

- **Overlapping subproblems.** `fib(n)` calls `fib(n - 1)` and `fib(n - 2)`, and `fib(n - 1)` calls `fib(n - 2)` again: the same small cases are solved many times, and the call tree roughly doubles at every level. The example's plain `fib_plain(25)` makes 242,785 calls for an answer that needs 25 different values.
- **Memoization** (top-down): keep a dict from arguments to answers, store each answer the first time, return it after that. `fib_memo(25)` makes 49 calls. `functools.lru_cache(maxsize=None)` does the same as a decorator (`cache_info()` shows 26 misses and 23 hits); its arguments must be **hashable**, because they are the dict's keys.
- **Bottom-up tables**: fill the smallest cases first in a loop and build up. No recursion, so no recursion limit, and often only the last row (for Fibonacci, the last two values) is needed: `fib_bottom_up(90)` is a loop of ninety steps.
- **Edit distance** (Levenshtein): the fewest single-character inserts, deletes and substitutions turning one string into another. `table[i][j]` is the distance between the first `i` characters of one and the first `j` of the other; the first row and column are lengths (all inserts or all deletes), and each other cell is the smallest of above plus one (delete), left plus one (insert) and diagonal plus one for a substitution, or plus nothing if the characters match. The corner is the answer; walking back along the choices lists the edits: kitten to sitting is 3 (substitute k with s, substitute e with i, insert g). It is the measure behind spell-checking, fuzzy matching and word error rate.
- **The knapsack** (0/1): items with weights and values, a capacity, and the most valuable set that fits. `best[i][room]` is the best value using the first `i` items in `room` capacity: either leave item `i` (the row above) or take it (the row above with its weight removed, plus its value). Walking back finds the chosen items. Four pieces of gear in a 9-kilo pack: the table finds stove, water and book worth 150; taking the most valuable first gives water and tent worth 130.
- **What makes a problem dynamic programming:** **optimal substructure** (the best answer is built from best answers to smaller versions) and **overlapping subproblems** (those smaller versions recur). Without overlap, plain recursion is fine (merge sort); when a local choice is provably safe, **greedy** is fine (Dijkstra's closest node); the knapsack is neither.
- **In machine learning:** the Viterbi algorithm that decodes the best sequence in a hidden Markov model, and the CTC loss that trains speech models, are tables exactly like these; beam search is the approximation used when the table would be too big; edit distance scores transcriptions as word error rate and aligns sequences; and the Bellman equation that reinforcement learning solves is dynamic programming over states.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/predict-the-call-counts.yaml",
    f'''id: predict-the-call-counts
type: predict_output
rev: 1
prompt: |
  The same Fibonacci function twice, once plain and once remembering its answers in a dict, each counting its calls. What does the program print?
code: |
{block(PREDICT_CALLS)}expected_output: |
{block(PREDICT_CALLS_OUT)}explanation: |
  Both give 55. The plain version makes 177 calls, because every call below the top makes two more and the small cases are reached many times; the memoized version makes 19, two per distinct value of `n` (one that computes it and one that finds it in the dict) minus one. The gap grows like `2` to the `n` against `2n`.
skills: [overlap]
''',
)

mcq(
    "mcq-why-exponential",
    "A plain recursive `fib(40)` takes a minute; `fib(41)` takes about a minute and a half. Why does each extra step cost so much, when there are only 41 different values to compute?",
    [
        "Because Python's recursion is slow, so any recursive function grows this way once it goes more than a few dozen levels deep",
        "Because the numbers get large and big-integer arithmetic dominates",
        "Because the function has no base case and only stops when the stack is full",
        "Because each call makes two more and the same small cases are reached again and again: the calls grow like 1.6 to the n",
    ],
    3,
    "`fib(40)` calls `fib(39)` and `fib(38)`, `fib(39)` calls `fib(38)` again, and so on: the tree of calls has about 1.6 to the 40 leaves, almost all of them repeats of the same handful of small cases. The arithmetic is cheap and the base case is fine; the waste is in solving the same subproblem again, which is what memoization removes.",
    ["overlap"],
)

write(
    "recall/parsons-a-memo-dict.yaml",
    "id: parsons-a-memo-dict\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to define a memoized Fibonacci and print `fib(50)`, `12586269025`. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("    if n in memo:")
    + "\nexplanation: |\n"
    + block("The base case comes first; then, if the answer isn't stored yet, compute it from the two smaller answers and store it; then return the stored answer. The decoy's `if n in memo:` would guard the computation the wrong way round, recomputing exactly the cases that were already known. Without the dict, `fib(50)` would make about 40 billion calls.")
    + "skills: [memo]\n",
)

mcq(
    "mcq-what-lru-cache-needs",
    "`@lru_cache(maxsize=None)` is put on a function that takes a list of numbers, and the first call raises `TypeError: unhashable type: 'list'`. Why, and what fixes it?",
    [
        "The cache is a dict keyed by the arguments, and a list can't be a key; pass a tuple instead",
        "The decorator only works on functions of one integer; split the list into separate arguments",
        "`maxsize=None` disables the cache; set a size to make it work",
        "The function must be recursive for `lru_cache` to apply",
    ],
    0,
    "Memoization stores answers under their arguments, so the arguments must be hashable, which a list is not because it can change. A tuple of the same numbers works. `maxsize=None` means keep everything, which is what memoization wants; the decorator works on any function, recursive or not.",
    ["memo"],
)

mcq(
    "mcq-one-cell-of-the-table",
    "In the edit-distance table, `table[i][j]` is the distance between the first `i` characters of `a` and the first `j` of `b`. How is it computed from its neighbours?",
    [
        "The sum of the cell above and the cell to the left, like a path count, since every edit path passes through one of them",
        "The diagonal cell plus 1, always, since every step is an edit",
        "The minimum of above plus 1, left plus 1, and diagonal plus 1 if the characters differ or plus 0 if they match",
        "The maximum of the three neighbours, because the distance can only grow",
    ],
    2,
    "Three ways to reach the pair of prefixes: delete `a`'s last character (from above), insert `b`'s last character (from the left), or line the two last characters up (from the diagonal), which costs a substitution unless they already match. The cheapest of the three is the distance; the first row and column seed it with plain lengths.",
    ["edit-distance"],
)

mcq(
    "mcq-what-makes-it-dynamic-programming",
    "Which of these is a dynamic-programming problem, rather than one that plain recursion or a greedy choice already solves well?",
    [
        "Sorting a list by splitting it in half and merging: the halves never overlap",
        "Finding the cheapest path with non-negative weights: settling the closest node is a safe greedy choice, so no table is needed",
        "Choosing the most valuable subset that fits a weight limit: best answers to smaller limits, which recur, build the answer",
        "Summing a list: one pass, nothing to remember",
    ],
    2,
    "Dynamic programming pays off when the best answer is built from best answers to smaller versions (optimal substructure) and those smaller versions come up again (overlap). The knapsack has both: each item's take-or-leave decision asks the same question at smaller capacities. Merge sort has no overlap; Dijkstra's greedy choice is provably safe; a sum has no subproblems worth remembering.",
    ["knapsack"],
)

write(
    "recall/review-predict-a-small-table.yaml",
    f'''id: review-predict-a-small-table
type: predict_output
rev: 1
prompt: |
  The edit-distance table for `ab` against `ac`, printed row by row. What does the program print?
code: |
{block(REVIEW_ROW)}expected_output: |
{block(REVIEW_ROW_OUT)}explanation: |
  The first row and column are lengths. `a` against `a` matches, so the middle cell is the diagonal 0 plus nothing. `ab` against `ac` differs in the last character, so the corner is the diagonal 0 plus one substitution: distance 1. The other cells are the cheapest of their three neighbours.
skills: [edit-distance]
''',
)

mcq(
    "review-mcq-top-down-or-bottom-up",
    "A memoized recursive function and a bottom-up table compute the same answers. When is the table the better choice?",
    [
        "Never; memoization is always faster because it skips subproblems the answer doesn't need, and the table computes them all",
        "When the arguments are unhashable, since a table has no keys",
        "Only for Fibonacci; other problems need recursion to express the recurrence",
        "When the input is long enough to hit the recursion limit, or when only the last row needs keeping",
    ],
    3,
    "Both do one piece of work per subproblem. Memoization follows the recursion, which can be deep enough to hit Python's limit on long inputs, and keeps every answer in its dict; a bottom-up loop has no depth and can throw away rows it no longer needs. Memoization's edge is skipping subproblems the answer never asks for; for Fibonacci and edit distance there are none.",
    ["memo"],
)

mcq(
    "review-mcq-greedy-fails",
    "Coins of 1, 15 and 25 must make 30 with as few coins as possible. Greedy takes the largest coin that fits each time. What happens?",
    [
        "Greedy takes 25 and then five 1s, six coins; the table finds 15 and 15, two",
        "Greedy finds 2 coins, 15 and 15, because it always finds the best for coin problems",
        "Greedy fails to make 30 at all, since 25 leaves 5 and there is no 5",
        "Greedy and the table both give 6, because 25 must be used",
    ],
    0,
    "Greedy commits to the 25 because it is the biggest step towards 30, and is then stuck making 5 from 1s. The table asks, for each amount from 1 to 30, the fewest coins given the answers for smaller amounts, and finds that 30 is 15 plus 15. Greedy happens to work for 1, 5, 10 and 25, which is why it feels right, and fails on other sets.",
    ["knapsack"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-fibonacci-edits-and-a-knapsack/exercise.yaml",
    f'''id: example-fibonacci-edits-and-a-knapsack
stage: worked_example
rev: 1
title: "Fibonacci, edits and a knapsack"
prompt: |
  A plain recursive Fibonacci counted against three ways of removing its waste, then two tables: the edit distance from kitten to sitting with its edits read back, and the best gear for a 9-kilo pack against the greedy choice. Press **Run**, then read how each part works.
steps:
  - label: "Plain recursion, counted"
    lines: "{ln('calls = 0')}-{ln('fib_plain(25) =')}"
    note: "The definition as a function: `fib(n)` is `fib(n - 1)` plus `fib(n - 2)`. Every call below the top makes two more, and the small cases are reached again and again: 242,785 calls for the 25th number. The same function on 40 would take a minute."
  - label: "Memoization with a dict"
    lines: "{ln('memo = ')}-{ln('fib_memo(25) =')}"
    note: "Before computing, look in the dict; after computing, store. Each value of `n` is computed once and found once more: 49 calls. The recursion is unchanged; only the repeats are gone."
  - label: "lru_cache: the same, as a decorator"
    lines: "{ln('@lru_cache')}-{ln('fib_cached(25) =')}"
    note: "The standard library's memoizer wraps the function: 26 misses (one per value, computed) and 23 hits (found). `maxsize=None` keeps everything; the arguments must be hashable, because they are the keys."
  - label: "Bottom-up, with two variables"
    lines: "{ln('def fib_bottom_up')}-{ln('fib_bottom_up(90) =')}"
    note: "Start from the smallest cases and build up in a loop, keeping only the last two values. No recursion, so no limit, and no table beyond two numbers: the 90th Fibonacci number in ninety steps."
  - label: "The edit-distance table"
    lines: "{ln('def edit_distance')}-{ln('    return table[len(a)][len(b)], table')}"
    note: "`table[i][j]` is the distance between the first `i` characters of `a` and the first `j` of `b`. The first row and column are lengths; each other cell is the cheapest of delete (above plus 1), insert (left plus 1) and substitute or match (diagonal plus 1, or plus 0 when the characters are the same). The corner is the answer."
  - label: "Reading the edits back"
    lines: "{ln('def edits')}-{ln('    return steps[::-1]')}"
    note: "From the corner, step to whichever neighbour produced the cell's value, recording an edit when it cost one, until the top-left. The steps come out backwards and are reversed."
  - label: "Kitten to sitting"
    lines: "{ln('distance, table = edit_distance')}-{ln('print(edits(')}"
    note: "Distance 3, and the table's seven rows: the corner reads 3. Walking back: substitute k with s, substitute e with i, insert g. Spell-checkers, fuzzy joins and word error rate all score strings this way."
  - label: "The knapsack table"
    lines: "{ln('def knapsack')}-{ln('    return best[len(items)][capacity], chosen[::-1]')}"
    note: "`best[i][room]` is the best value from the first `i` items with `room` capacity: leave item `i` (the row above) or take it (the row above with its weight removed, plus its value). Walking back from the corner finds which items were taken: wherever the value changed from the row above, the item is in the pack."
  - label: "Table against greedy"
    lines: "{ln('gear = [')}-{ln('greedy by value:')}"
    note: "Stove, water and book weigh 9 and are worth 150. Taking the most valuable item first gives water and tent, also 9 kilos, worth 130: the greedy choice of the tent blocks the better combination. That is why the knapsack needs the table."
''',
)
write("exercises/example-fibonacci-edits-and-a-knapsack/solution.py", EXAMPLE)
write(
    "exercises/example-fibonacci-edits-and-a-knapsack/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the four Fibonacci lines, the edit distance with its table and edits, and the knapsack against greedy."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-paths-through-a-grid/exercise.yaml",
    f'''id: fill-paths-through-a-grid
stage: fill_in
rev: 1
title: "Paths through a grid"
prompt: |
  `paths(rows, cols)` counts the ways to walk from the top-left corner of a grid to the bottom-right moving only right or down: the ways from a cell are the ways from below it plus the ways from its right, and an edge cell has one. Plain recursion repeats the same cells millions of times; replace each `...` so the answers are remembered in `memo`, and the program prints:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "The key for a cell is the pair `(rows, cols)`; check whether it is already in `memo` before computing."
  - "Return the stored answer, `memo[(rows, cols)]`, whether it was just computed or found."
skills: [memo]
''',
)
write("exercises/fill-paths-through-a-grid/starter.py", FILL_STARTER)
write("exercises/fill-paths-through-a-grid/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-paths-through-a-grid/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the three path counts."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_a_big_grid():
    """A 30 by 30 grid has 118264581564861424 paths, which only a memoized version can count in time."""
    paths = function("paths")
    assert paths(30, 30) == 118264581564861424
''',
)
write("exercises/fill-paths-through-a-grid/wrong/edge-is-zero.py", FILL_WRONG)
write(
    "exercises/fill-paths-through-a-grid/wrong/typed-in.py",
    "def paths(rows, cols):\n    return 6\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-fewest-coins/exercise.yaml",
    f'''id: write-fewest-coins
stage: write
rev: 1
title: "The fewest coins"
prompt: |
  Write `min_coins(coins, amount)`, the fewest coins (any coin may be used many times) that add up to `amount`, or `-1` if no combination does, with a bottom-up table: `best[total]` is the fewest coins for `total`, starting from `best[0] = 0`, and for each total the best over every coin that fits of `best[total - coin] + 1`. Then print it for these calls:

  ```python
  print(min_coins([1, 5, 10, 25], 63))
  print(min_coins([1, 15, 25], 30))
  print(min_coins([4, 7], 10))
  ```

  ```
{block(WRITE_OUT)}  ```

  Greedy (largest coin first) gets the first right and the second wrong, which is the point.
hints:
  - "Start every total above 0 at `float(\\"inf\\")`, so that an impossible total stays infinite and a possible one is improved."
  - "At the end, an infinite `best[amount]` means no combination exists: return -1."
skills: [knapsack]
''',
)
write("exercises/write-fewest-coins/starter.py", "")
write("exercises/write-fewest-coins/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-fewest-coins/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints 6, 2 and -1."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_more_amounts():
    """Zero needs no coins; 3, 7 and 405 make 13 with three coins; 2 can't be made from 3s."""
    min_coins = function("min_coins")
    assert min_coins([1, 2], 0) == 0
    assert min_coins([3, 7, 405], 13) == 3
    assert min_coins([3], 2) == -1
    assert min_coins([9, 6, 5, 1], 11) == 2
''',
)
write("exercises/write-fewest-coins/wrong/greedy.py", WRITE_GREEDY)
write(
    "exercises/write-fewest-coins/wrong/typed-in.py",
    "def min_coins(coins, amount):\n    return 6\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-three-tables/exercise.yaml",
    f'''id: build-three-tables
stage: build
rev: 1
title: "Three tables"
prompt: |
  Starting from a blank editor, write four functions:

  - `fib(n)`: the n-th Fibonacci number (`fib(0)` is 0, `fib(1)` is 1), bottom-up, so that `fib(500)` works.
  - `edit_distance(a, b)`: the fewest single-character inserts, deletes and substitutions turning `a` into `b`, by the table.
  - `knapsack(items, capacity)`: for a list of `(name, weight, value)` and an integer capacity, the tuple `(best value, names of the chosen items in the order given)`, by the table over items and capacity.
  - `min_coins(coins, amount)`: the fewest coins that make the amount, or `-1`.

  Then print:

  ```python
  print(fib(10), fib(90))
  print(edit_distance("kitten", "sitting"), edit_distance("", "abc"), edit_distance("flaw", "lawn"))
  gear = [("tent", 5, 60), ("stove", 3, 50), ("water", 4, 70), ("book", 2, 30)]
  print(knapsack(gear, 9))
  print(min_coins([1, 5, 10, 25], 63), min_coins([1, 15, 25], 30), min_coins([4, 7], 10))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks include `fib(500)`, longer strings, a knapsack where the most valuable item is the wrong choice, and coins where greedy fails.
skills: [memo, edit-distance, knapsack]
''',
)
write("exercises/build-three-tables/starter.py", "")
write("exercises/build-three-tables/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-three-tables/test_exercise.py",
    f'''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the four lines."""
    assert run() == {BUILD_OUT!r}


def test_fib_500():
    """fib(500) is the 105-digit number starting 139423224561697880."""
    fib = function("fib")
    value = fib(500)
    assert len(str(value)) == 105 and str(value).startswith("139423224561697880") and fib(2) == 1


def test_edit_distance():
    """intention to execution is 5, the distance is symmetric, and identical strings are 0."""
    edit_distance = function("edit_distance")
    assert edit_distance("intention", "execution") == 5
    assert edit_distance("sunday", "saturday") == 3 and edit_distance("saturday", "sunday") == 3
    assert edit_distance("same", "same") == 0


def test_knapsack_beats_greedy():
    """With capacity 10, one item of weight 10 worth 60 loses to two items of weight 5 worth 35 each, and an empty list fits nothing."""
    knapsack = function("knapsack")
    items = [("big", 10, 60), ("left", 5, 35), ("right", 5, 35)]
    assert knapsack(items, 10) == (70, ["left", "right"])
    assert knapsack([], 10) == (0, [])
    assert knapsack(items, 4) == (0, [])


def test_min_coins():
    """9, 6, 5 and 1 make 11 with two coins, not five."""
    min_coins = function("min_coins")
    assert min_coins([9, 6, 5, 1], 11) == 2 and min_coins([2], 3) == -1 and min_coins([2], 0) == 0
''',
)
write("exercises/build-three-tables/wrong/no-match-discount.py", BUILD_NO_MATCH_DISCOUNT)
write("exercises/build-three-tables/wrong/greedy-knapsack.py", BUILD_GREEDY_KNAPSACK)
write("exercises/build-three-tables/wrong/greedy-coins.py", BUILD_GREEDY_COINS)
write(
    "exercises/build-three-tables/wrong/typed-in.py",
    "def fib(n):\n    return 55\n\n\ndef edit_distance(a, b):\n    return 3\n\n\ndef knapsack(items, capacity):\n    return (150, ['stove', 'water', 'book'])\n\n\ndef min_coins(coins, amount):\n    return 6\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-an-edit-distance/exercise.yaml",
    f'''id: debug-an-edit-distance
stage: debug
rev: 1
title: "An edit distance that is too cheap"
prompt: |
  `edit_distance(a, b)` should print the distance for four pairs:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the empty string to `abc` costs 0 and kitten to sitting only {STARTER_LINES[0].split()[-1]}, because the table's first row and column are never filled in: turning the first `i` characters into nothing costs `i` deletes, and nothing into the first `j` characters costs `j` inserts. Fix that, and `same` to `same` costs {COST_LINES[3].split()[-1]} and kitten to sitting {COST_LINES[0].split()[-1]}: the diagonal step charges a substitution even when the two characters already match, and a match should cost nothing.
skills: [edit-distance]
''',
)
write("exercises/debug-an-edit-distance/starter.py", DEBUG_STARTER)
write("exercises/debug-an-edit-distance/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-an-edit-distance/test_exercise.py",
    f'''from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the four distances."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_more_pairs():
    """abc to nothing is 3, sunday to saturday is 3, and a one-letter substitution is 1."""
    edit_distance = function("edit_distance")
    assert edit_distance("abc", "") == 3 and edit_distance("sunday", "saturday") == 3 and edit_distance("cat", "cut") == 1
''',
)
write("exercises/debug-an-edit-distance/wrong/still-no-edges.py", DEBUG_STILL_NO_EDGES)
write("exercises/debug-an-edit-distance/wrong/still-charges-matches.py", DEBUG_STILL_ALWAYS_COST)
write(
    "exercises/debug-an-edit-distance/wrong/typed-in.py",
    "def edit_distance(a, b):\n    return 3\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-climb-stairs/exercise.yaml",
    f'''id: review-climb-stairs
stage: review_code
rev: 1
title: "Climbing stairs, from memory"
prompt: |
  Write `ways(n)`, the number of ways to climb `n` stairs taking one or two steps at a time (`ways(0)` is 1: stay put), bottom-up with two variables, and print it for 1, 2, 5 and 30:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [memo]
''',
)
write("exercises/review-climb-stairs/starter.py", "")
write("exercises/review-climb-stairs/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-climb-stairs/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints 1 2 8 1346269."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_more_stairs():
    """ways(0) is 1, ways(3) is 3, and ways(80) is 37889062373143906, which only a non-exponential version reaches."""
    ways = function("ways")
    assert ways(0) == 1 and ways(3) == 3 and ways(80) == 37889062373143906
''',
)
write(
    "exercises/review-climb-stairs/wrong/off-by-one.py",
    REVIEW_CODE_SOLUTION.replace("    return one_below", "    return here"),
)
write(
    "exercises/review-climb-stairs/wrong/typed-in.py",
    "def ways(n):\n    return 8\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.dsa.dynamic-programming written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
