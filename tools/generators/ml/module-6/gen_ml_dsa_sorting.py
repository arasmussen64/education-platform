"""Writes the topic ml.dsa.sorting-and-searching (Module 6's fourth topic).
Run from the repository root under uv (python -m uv run python <this file>),
so every program's expected output is captured from CPython rather than typed
in. Comparison counts come from the topic's own sorts, so they are the same in
both runtimes; Python's sorted is described, not counted. Files are written as
bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.dsa.sorting-and-searching")


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

EXAMPLE = '''import bisect
import random

import numpy as np


def binary_search(items, target, counter):
    """The index of target in a sorted list, or -1: look in the middle, keep the half that can hold it."""
    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        counter[0] += 1
        if items[mid] == target:
            return mid
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def scan(items, target, counter):
    for i, item in enumerate(items):
        counter[0] += 1
        if item == target:
            return i
    return -1


evens = list(range(0, 2_000_000, 2))
for name, search in (("scan", scan), ("binary search", binary_search)):
    counter = [0]
    found = search(evens, 1_999_998, counter)
    missing = search(evens, 1_999_999, counter)
    print(name + ": found at", found, "and missing is", missing, "after", counter[0], "comparisons")


def insertion_sort(items, counter):
    """Grow a sorted front: each item shifts left past the larger ones and stops."""
    result = list(items)
    for i in range(1, len(result)):
        value = result[i]
        j = i - 1
        while j >= 0:
            counter[0] += 1
            if result[j] <= value:
                break
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = value
    return result


def merge_sort(items, counter):
    """Split in half, sort each half the same way, merge the two sorted halves."""
    if len(items) <= 1:
        return list(items)
    middle = len(items) // 2
    left = merge_sort(items[:middle], counter)
    right = merge_sort(items[middle:], counter)
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        counter[0] += 1
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


for n in (1000, 2000):
    data = list(range(n))
    random.Random(1).shuffle(data)
    counts = {}
    for name, sort in (("insertion", insertion_sort), ("merge", merge_sort)):
        counter = [0]
        assert sort(data, counter) == list(range(n))
        counts[name] = counter[0]
    print(n, "shuffled items:", counts)
counter = [0]
insertion_sort(list(range(2000)), counter)
print("2000 already sorted items: insertion", counter[0])

records = [("Oslo", 30), ("Lima", 12), ("Oslo", 8), ("Pune", 19), ("Lima", 41)]
print(sorted(records, key=lambda record: record[0]))
print(sorted(records, key=lambda record: (record[0], -record[1])))

bands = [50, 65, 80, 90]
for score in (49, 65, 79, 95):
    print(score, "is in band", bisect.bisect_right(bands, score))

names = np.array(["ann", "bob", "cy", "dee"])
scores = np.array([71, 93, 58, 93])
order = np.argsort(-scores, kind="stable")
print(order, names[order])
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
SCAN_COMPARED = int(EX[0].split()[-2])
BINARY_COMPARED = int(EX[1].split()[-2])
assert EX[0].startswith("scan: found at 999999 and missing is -1 after") and SCAN_COMPARED == 2_000_000, EX[0]
assert EX[1].startswith("binary search: found at 999999 and missing is -1 after") and BINARY_COMPARED <= 45, EX[1]
COUNTS = {}
for line in EX[2:4]:
    n = int(line.split()[0])
    COUNTS[n] = eval(line.split(":", 1)[1])
INSERTION_RATIO = COUNTS[2000]["insertion"] / COUNTS[1000]["insertion"]
MERGE_RATIO = COUNTS[2000]["merge"] / COUNTS[1000]["merge"]
assert 3.7 <= INSERTION_RATIO <= 4.3 and 2.1 <= MERGE_RATIO <= 2.3, (INSERTION_RATIO, MERGE_RATIO)
assert EX[4] == "2000 already sorted items: insertion 1999", EX[4]
assert EX[5] == "[('Lima', 12), ('Lima', 41), ('Oslo', 30), ('Oslo', 8), ('Pune', 19)]", EX[5]
assert EX[6] == "[('Lima', 41), ('Lima', 12), ('Oslo', 30), ('Oslo', 8), ('Pune', 19)]", EX[6]
assert EX[7:11] == ["49 is in band 0", "65 is in band 2", "79 is in band 2", "95 is in band 4"], EX[7:11]
assert EX[11] == "[1 3 0 2] ['bob' 'dee' 'ann' 'cy']", EX[11]
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


def thousands(n: int) -> str:
    return f"{n:,}"


# --- recall programs ----------------------------------------------------------------------------

PREDICT_BINARY = '''items = [2, 3, 5, 7, 11, 13, 17, 19]
lo, hi = 0, len(items) - 1
while lo <= hi:
    mid = (lo + hi) // 2
    print("looking at index", mid, "value", items[mid])
    if items[mid] == 13:
        break
    if items[mid] < 13:
        lo = mid + 1
    else:
        hi = mid - 1
'''
PREDICT_BINARY_OUT = out(PREDICT_BINARY)
assert PREDICT_BINARY_OUT == "looking at index 3 value 7\nlooking at index 5 value 13\n", PREDICT_BINARY_OUT

PREDICT_STABLE = '''records = [("b", 2), ("a", 1), ("c", 2), ("d", 1)]
print([name for name, score in sorted(records, key=lambda r: r[1])])
print([name for name, score in sorted(records, key=lambda r: r[1], reverse=True)])
'''
PREDICT_STABLE_OUT = out(PREDICT_STABLE)
assert PREDICT_STABLE_OUT == "['a', 'd', 'b', 'c']\n['b', 'c', 'a', 'd']\n", PREDICT_STABLE_OUT

REVIEW_BISECT = '''import bisect

grades = [60, 70, 80, 90]
for score in (59, 60, 85, 100):
    print(score, bisect.bisect_right(grades, score))
'''
REVIEW_BISECT_OUT = out(REVIEW_BISECT)
assert REVIEW_BISECT_OUT == "59 0\n60 1\n85 3\n100 4\n", REVIEW_BISECT_OUT

PARSONS_LINES = [
    'records = [("ann", 3), ("bob", 1), ("cy", 2)]',
    "by_score = sorted(records, key=lambda record: record[1])",
    "print([name for name, score in by_score])",
]
assert out("\n".join(PARSONS_LINES) + "\n") == "['bob', 'cy', 'ann']\n"

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''def merge(left, right):
    """Combine two sorted lists into one sorted list in a single pass."""
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


print(merge([1, 4, 9], [2, 3, 10, 11]))
print(merge([], [5, 6]))
print(merge([2, 2], [2]))
'''
FILL_STARTER = FILL_SOLUTION.replace("if left[i] <= right[j]:", "if left[i] <= right[...]:").replace("    merged.extend(left[i:])\n", "    merged.extend(...)\n")
FILL_WRONG = FILL_SOLUTION.replace("    merged.extend(right[j:])\n", "")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "[1, 2, 3, 4, 9, 10, 11]\n[5, 6]\n[2, 2, 2]\n", FILL_OUT
assert out(FILL_WRONG) != FILL_OUT

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''def binary_search(items, target):
    """The index of target in a sorted list, or -1."""
    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
print(binary_search(primes, 2), binary_search(primes, 29), binary_search(primes, 13))
print(binary_search(primes, 4), binary_search([], 1))
'''
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "0 9 5\n-1 -1\n", WRITE_OUT
WRITE_SCAN = WRITE_SOLUTION.replace(
    '''    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1''',
    '''    for i, item in enumerate(items):
        if item == target:
            return i
    return -1''',
)
WRITE_OFF_BY_ONE = WRITE_SOLUTION.replace("while lo <= hi:", "while lo < hi:")
assert out(WRITE_SCAN) == WRITE_OUT and out(WRITE_OFF_BY_ONE) != WRITE_OUT

TRACKED = '''

class Tracked:
    """A value that counts how often it is compared, whichever comparison is used."""

    compared = 0

    def __init__(self, value):
        self.value = value

    def _count(self):
        Tracked.compared += 1

    def __eq__(self, other):
        self._count()
        return self.value == other.value

    def __lt__(self, other):
        self._count()
        return self.value < other.value

    def __le__(self, other):
        self._count()
        return self.value <= other.value

    def __gt__(self, other):
        self._count()
        return self.value > other.value

    def __ge__(self, other):
        self._count()
        return self.value >= other.value

    def __hash__(self):
        return hash(self.value)


def tracked(values):
    return [Tracked(v) for v in values]


def values(items):
    return [item.value for item in items]
'''

# --- the build ----------------------------------------------------------------------------------

BUILD_SOLUTION = '''def insertion_sort(items):
    """A new sorted list: each item shifts left past the larger ones and stops at the first that isn't."""
    result = list(items)
    for i in range(1, len(result)):
        value = result[i]
        j = i - 1
        while j >= 0 and result[j] > value:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = value
    return result


def merge_sort(items):
    """A new sorted list: split in half, sort each half, merge."""
    if len(items) <= 1:
        return list(items)
    middle = len(items) // 2
    left = merge_sort(items[:middle])
    right = merge_sort(items[middle:])
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def binary_search(items, target):
    """The index of target in a sorted list, or -1."""
    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def top_k_by(records, field, k):
    """The k records with the largest field value, largest first; ties keep their original order."""
    return sorted(records, key=lambda record: record[field], reverse=True)[:k]


print(insertion_sort([5, 2, 9, 1, 5, 6]), merge_sort([5, 2, 9, 1, 5, 6]))
print(binary_search([1, 3, 5, 7, 9], 7), binary_search([1, 3, 5, 7, 9], 4))
scores = [{"name": "ann", "score": 71}, {"name": "bob", "score": 93}, {"name": "cy", "score": 58}, {"name": "dee", "score": 93}]
print([record["name"] for record in top_k_by(scores, "score", 3)])
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == "[1, 2, 5, 5, 6, 9] [1, 2, 5, 5, 6, 9]\n3 -1\n['bob', 'dee', 'ann']\n", BUILD_OUT
BUILD_INSERTION_FROM_LEFT = BUILD_SOLUTION.replace(
    '''    result = list(items)
    for i in range(1, len(result)):
        value = result[i]
        j = i - 1
        while j >= 0 and result[j] > value:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = value
    return result''',
    '''    result = []
    for value in items:
        position = 0
        while position < len(result) and result[position] <= value:
            position += 1
        result.insert(position, value)
    return result''',
)
BUILD_MERGE_IS_INSERTION = BUILD_SOLUTION.replace(
    '''    if len(items) <= 1:
        return list(items)
    middle = len(items) // 2
    left = merge_sort(items[:middle])
    right = merge_sort(items[middle:])
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged''',
    "    return insertion_sort(items)",
)
BUILD_SCAN_SEARCH = BUILD_SOLUTION.replace(
    '''    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1''',
    '''    for i, item in enumerate(items):
        if item == target:
            return i
    return -1''',
)
BUILD_TOP_K_ASCENDING = BUILD_SOLUTION.replace("reverse=True)[:k]", ")[:k]")
for wrong in (BUILD_INSERTION_FROM_LEFT, BUILD_MERGE_IS_INSERTION, BUILD_SCAN_SEARCH):
    assert wrong != BUILD_SOLUTION and out(wrong) == BUILD_OUT, "these pass the printed output and fail the counts"
assert out(BUILD_TOP_K_ASCENDING) != BUILD_OUT

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''def binary_search(items, target):
    """The index of target in a sorted list, or -1."""
    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


readings = [41, 7, 19, 73, 2, 56, 30, 88, 64, 11]
ordered = sorted(readings)
print(ordered)
for target in (2, 30, 88, 50):
    print(target, "at index", binary_search(ordered, target))
'''
BUG_UNSORTED = ("binary_search(ordered, target)", "binary_search(readings, target)")
BUG_LOOP = ("    while lo <= hi:", "    while lo < hi:")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_UNSORTED).replace(*BUG_LOOP)
DEBUG_STILL_UNSORTED = DEBUG_SOLUTION.replace(*BUG_UNSORTED)
DEBUG_STILL_LOOP = DEBUG_SOLUTION.replace(*BUG_LOOP)
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT + "starter:\n" + out(DEBUG_STARTER) + "loop only:\n" + out(DEBUG_STILL_LOOP))
assert DEBUG_OUT == "[2, 7, 11, 19, 30, 41, 56, 64, 73, 88]\n2 at index 0\n30 at index 4\n88 at index 9\n50 at index -1\n", DEBUG_OUT
assert out(DEBUG_STILL_UNSORTED).splitlines()[1:3] == ["2 at index 4", "30 at index -1"], out(DEBUG_STILL_UNSORTED)
assert out(DEBUG_STILL_LOOP).splitlines()[1:4] == ["2 at index -1", "30 at index 4", "88 at index -1"], out(DEBUG_STILL_LOOP)
assert out(DEBUG_STARTER) != DEBUG_OUT

REVIEW_CODE_SOLUTION = WRITE_SOLUTION
REVIEW_CODE_OUT = WRITE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.dsa.sorting-and-searching
kind: topic
status: ready
title: "Sorting and searching"
summary: "Binary search on sorted data, insertion sort and merge sort written and counted, why n log n is the floor for sorting by comparisons, Python's sorted with keys, and NumPy's argsort."
prerequisites: [ml.dsa.stacks-queues-recursion]
packages: [numpy]
estimated_minutes: 55
rev: 1
objectives:
  - "Write binary search, and say why it needs sorted data and takes log n steps."
  - "Write insertion sort and merge sort, and count their comparisons to see n² against n log n."
  - "Sort by a key and by several keys with sorted, and say why Python's sort being stable matters."
  - "Use np.argsort to order one array by another, and bisect to search a sorted list."
# Linked, never copied or embedded: the Runestone book is CC BY-NC-SA 4.0;
# the Python documentation is under the PSF licence; NumPy's documentation
# is under the NumPy licence (BSD-3-Clause).
resources:
  - title: "Problem Solving with Algorithms and Data Structures using Python (Brad Miller and David Ranum), chapter 6: Sorting and Searching, sections 6.3 and 6.4 (sequential and binary search), 6.9 (insertion sort) and 6.11 (merge sort)"
    url: https://runestone.academy/ns/books/published/pythonds3/SortSearch/toctree.html
    type: reading
    use: link
    license: CC BY-NC-SA 4.0
  - title: "The Python documentation: Sorting Techniques (key functions, sort stability, reverse)"
    url: https://docs.python.org/3/howto/sorting.html
    type: reading
    use: link
    license: "PSF licence (linked, not copied)"
  - title: "numpy.argsort (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/generated/numpy.argsort.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-search-and-sort-counted
  - predict-a-binary-search
  - mcq-why-sorted-first
  - mcq-a-million-items
  - parsons-sort-by-score
  - predict-a-stable-sort
  - mcq-what-stable-buys
  - mcq-what-argsort-returns
  - fill-merge-two-sorted-lists
  - write-binary-search
prove:
  build: build-sort-and-search
  debug: debug-a-search-that-misses
  explain:
    prompt: |
      A teammate looks up each of 50,000 customer ids in a list of 2 million records with a scan, and sorts a leaderboard by score with a sort they wrote themselves, which sometimes shuffles customers who have equal scores. In your own words: how does binary search find an item in a sorted list, how many steps does it take on 2 million items, and what must be true of the data first? Why does merge sort take about n log n comparisons where insertion sort takes about n², and when is insertion sort the better choice anyway? What does it mean that Python's sort is stable, and why does that fix the leaderboard? And how would you decide between sorting the records once and searching, and putting them in a dict?
    rubric:
      - id: binary-search
        required: true
        description: "Look at the middle element, keep the half that can hold the target, repeat: each step halves the candidates, so about log2 n steps, 21 for 2 million; the list must be sorted and support indexing."
      - id: sorts
        required: true
        description: "Merge sort splits in halves (log n levels) and merges each level in n steps, so n log n; insertion sort shifts each item past the larger ones, about n²/4 on random data; insertion sort wins on small or nearly sorted input, where it makes about n comparisons."
      - id: keys
        required: true
        description: "Stable means items with equal keys keep their original order, so sorting by score keeps the earlier customer first among ties and sorting in passes (or by a tuple key) gives a multi-key order; Python's sorted is stable and takes a key function."
      - id: choose
        required: true
        description: "Sorting once costs n log n and each search log n: 50,000 searches of 2 million is about 44 million steps after a 42-million-step sort, against a dict's one pass to build and one step per lookup; the dict wins for exact lookups, the sorted list for ranges, neighbours and order."
    model_answer: |
      Binary search works on a sorted list by looking at the middle element: if it is the target, done; if it is smaller, the target can only be in the right half; otherwise only in the left half. Each step halves the candidates, so on 2 million items it takes about 21 steps, where a scan takes up to 2 million. The data must be sorted first, and it must be something you can index into directly, like a list or an array, not a chain you have to walk. Merge sort is about n log n because it splits the list in half repeatedly, which takes log n levels, and at each level merges pairs of sorted halves in one pass over all n items. Insertion sort grows a sorted front and shifts each new item left past the items larger than it, which on random data is about a quarter of n squared comparisons. But on data that is already nearly sorted each item stops almost at once, so insertion sort makes about n comparisons, and for small lists its simplicity beats merge sort's overhead; Python's own sort uses it for short runs. Stable means that items whose keys compare equal keep the order they had before the sort. The leaderboard shuffles tied customers because the hand-written sort isn't stable; Python's sorted is, so sorting by score keeps the earlier customer first among ties, and sorting by several keys can be done with a tuple key or in passes from the least important key to the most. For the lookups, sorting the records once costs about n log n, around 42 million steps for 2 million records, and then each of the 50,000 searches costs about 21 steps, under a million more. A dict costs one pass to build and one step per lookup. For exact-match lookups the dict is simpler and faster; the sorted list earns its keep when I also need ranges, nearest neighbours, or the records in order.
review_pool:
  - review-predict-bisect
  - review-mcq-sort-once-or-dict
  - review-mcq-the-merge-step
  - review-binary-search
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: binary-search
    description: "Write binary search, and say why it needs sorted data and takes log n steps"
  - id: sorts
    description: "Write insertion sort and merge sort, and count n² against n log n"
  - id: keys
    description: "Sort by one or several keys with sorted, and say why stability matters"
  - id: numpy-sort
    description: "Order one array by another with argsort, and search a sorted list with bisect"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

Two of the oldest algorithms, and the first ones in this module whose cost you can feel: **binary search**, which finds an item in a sorted list of a million in twenty steps, and **sorting**, where the difference between a quadratic method and an `n log n` one is the difference between a second and an hour. The worked example writes both searches and both sorts and counts their comparisons, then shows what Python gives you for free: `sorted` with keys and stability, `bisect`, and NumPy's `argsort`.

The main resource is **_Problem Solving with Algorithms and Data Structures using Python_, chapter 6**: the sequential and binary searches (6.3, 6.4), insertion sort (6.9) and merge sort (6.11); about 40 minutes with runnable code and animations. The Python documentation's _Sorting Techniques_ is the reference for `key=` and stability. Watch for:

- **Halving** is what makes binary search logarithmic.
- **The merge step** is linear, and there are `log n` levels of it.
- **Insertion sort on sorted input** makes one comparison per item.

</Intro>

<Resource index={{0}} />

<Recap>

- **Binary search** on a sorted list: look at the middle, keep the half that can hold the target, repeat. Each step halves the candidates, so it takes about `log2 n` steps: the example finds a value among a million in {BINARY_COMPARED // 2} comparisons and rules one out in {BINARY_COMPARED - BINARY_COMPARED // 2}, where a scan takes {thousands(SCAN_COMPARED // 2)} each. It needs data that is **sorted** and **indexable** (a list or an array, not a chain). `bisect.bisect_right(sorted_list, x)` is binary search from the standard library: the index where `x` would be inserted, which is also how many thresholds `x` has reached, so a score of 79 against bands at 50, 65, 80 and 90 is in band 2.
- **Insertion sort** grows a sorted front: each new item shifts left past the larger ones and stops at the first that isn't. About `n² / 4` comparisons on shuffled data ({thousands(COUNTS[1000]["insertion"])} for 1,000 items, {thousands(COUNTS[2000]["insertion"])} for 2,000: times {INSERTION_RATIO:.1f} on doubling), but only `n - 1` on data already in order ({thousands(1999)} for 2,000), which is why it is the right sort for small or nearly sorted input.
- **Merge sort** splits the list in half, sorts each half the same way (recursion, from the last topic), and **merges** the two sorted halves in one pass. There are `log2 n` levels of splitting and each level's merges touch all `n` items, so about `n log2 n` comparisons: {thousands(COUNTS[1000]["merge"])} for 1,000 and {thousands(COUNTS[2000]["merge"])} for 2,000, times {MERGE_RATIO:.1f} on doubling. That is the floor for sorting by comparisons: `n` items have `n!` orderings, each comparison can at best halve them, and `log2(n!)` is about `n log2 n`.
- **Python's `sorted`** (and `list.sort`) is **Timsort**: merge sort that finds runs already in order and insertion-sorts short ones, `n log n` at worst and about `n` on sorted input. `key=` computes each item's sort key once (`key=lambda r: r[1]`, or a tuple for several keys, `-value` to reverse one of them); `reverse=True` reverses. It is **stable**: items with equal keys keep their original order, so sorting by city keeps each city's records in the order they came, and sorting in passes from the least important key to the most gives a multi-key order.
- **NumPy** sorts arrays with `np.sort`, and `np.argsort(scores)` returns the **indices** that would sort them, so `names[np.argsort(-scores, kind="stable")]` lists the names from the highest score down, ties in their original order. `np.searchsorted` is bisect for arrays.
- **In machine learning:** `argsort` is how top-k predictions, rankings and nearest neighbours are read off a vector of scores; a stable sort by a key is every leaderboard and every "group by then order"; binary search on sorted thresholds turns a score into a band; and "sort once, search many times" against "build a dict" is a choice the counts decide: sort for order, ranges and neighbours, a dict for exact lookups.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/predict-a-binary-search.yaml",
    f'''id: predict-a-binary-search
type: predict_output
rev: 1
prompt: |
  A binary search for 13 that prints every index it looks at. What does the program print?
code: |
{block(PREDICT_BINARY)}expected_output: |
{block(PREDICT_BINARY_OUT)}explanation: |
  Eight items: the middle index is `(0 + 7) // 2 = 3`, value 7, too small, so the search keeps indices 4 to 7. Their middle is `(4 + 7) // 2 = 5`, value 13: found in two looks. Each look halves what is left, which is why eight items need at most three looks and a million need about twenty.
skills: [binary-search]
''',
)

mcq(
    "mcq-why-sorted-first",
    "Why does binary search need the list to be sorted, and what happens if it isn't?",
    [
        "Because the middle element has to be the median for the halving to be fair, which only sorting guarantees",
        "It doesn't; sorting just makes the search a little faster on average, because likely values sit in the middle",
        "Because the comparison with the middle only says which half can hold the target when the halves are ordered",
        "Because an unsorted list has no middle element, so `(lo + hi) // 2` is undefined",
    ],
    2,
    "The whole method is throwing away half the list after one comparison, and that is only safe when the half thrown away cannot contain the target, which is what sorted order guarantees. On an unsorted list the search may discard the half that holds the target and report it missing, as the debug exercise shows.",
    ["binary-search"],
)

mcq(
    "mcq-a-million-items",
    "Merge sort makes about `n log2 n` comparisons and insertion sort about `n² / 4` on shuffled data. On a million items, roughly how many is each?",
    [
        "Merge sort about 20 million; insertion sort about 250 billion",
        "Merge sort about a million; insertion sort about 20 million, so both are fine on a modern machine",
        "Merge sort about 20 million; insertion sort about 4 million, because the quarter helps it",
        "Both about a million, since each item is compared once per pass",
    ],
    0,
    "`log2` of a million is about 20, so merge sort makes about 20 million comparisons, a fraction of a second. A million squared is a million million; a quarter of that is 250 billion, hours of work. The constant in front doesn't rescue a quadratic once `n` is large; only the order does.",
    ["sorts"],
)

write(
    "recall/parsons-sort-by-score.yaml",
    "id: parsons-sort-by-score\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to sort three records by their score and print the names in that order, `['bob', 'cy', 'ann']`. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("by_score = sorted(records, key=lambda record: record[0])")
    + "\nexplanation: |\n"
    + block("`key=` names the value to sort by: `record[1]` is the score, so bob (1), cy (2), ann (3). The decoy sorts by `record[0]`, the name, which would print the names alphabetically. The key function is called once per record and the records themselves are left unchanged.")
    + "skills: [keys]\n",
)

write(
    "recall/predict-a-stable-sort.yaml",
    f'''id: predict-a-stable-sort
type: predict_output
rev: 1
prompt: |
  Four records sorted by score, then sorted by score in reverse. Two records share each score. What does the program print?
code: |
{block(PREDICT_STABLE)}expected_output: |
{block(PREDICT_STABLE_OUT)}explanation: |
  Python's sort is stable: records with equal keys keep the order they had. Score 1 holds `a` then `d` (their original order), score 2 holds `b` then `c`. `reverse=True` reverses the order of the keys, not of the ties: the 2s come first, still as `b` then `c`.
skills: [keys]
''',
)

mcq(
    "mcq-what-stable-buys",
    "A leaderboard is sorted by score, and customers with equal scores should stay in the order they signed up. What property of the sort makes that work, and how do you also sort by name within a score?",
    [
        "Stability: equal keys keep their original order; name within score is the key `(-score, name)`",
        "Determinism: a sort always gives the same output for the same input, so ties stay where they were",
        "Speed: a fast sort has no time to move the ties around, so they stay in sign-up order",
        "Uniqueness: the sort removes duplicate scores so there are no ties left to order",
    ],
    0,
    "A stable sort promises that items whose keys compare equal come out in the order they went in, which is exactly the sign-up order if the list was in that order. Two keys can be combined in one tuple, or applied in two passes from the least important key to the most, because each later pass keeps the earlier order among its ties. Determinism alone would allow a stable-looking shuffle.",
    ["keys"],
)

mcq(
    "mcq-what-argsort-returns",
    "`scores = np.array([71, 93, 58])` and `names = np.array([\"ann\", \"bob\", \"cy\"])`. What is `np.argsort(scores)`, and how does it order the names?",
    [
        "`[58, 71, 93]`, the sorted scores; `names` has to be sorted separately with its own call",
        "`[1, 0, 2]`, the rank of each score; `names[ranks]` reorders the names by rank",
        "`[0, 1, 2]`, because argsort returns positions, and positions are already in order whatever the scores are",
        "`[2, 0, 1]`, the indices that would sort the scores; indexing `names` with it gives `cy, ann, bob`",
    ],
    3,
    "`argsort` doesn't move the scores; it says where the smallest, then the next, are: index 2 (58), index 0 (71), index 1 (93). Indexing any other array with that result orders it the same way, which is how one array is ordered by another. Ranks are the inverse of that, and `np.sort` is the one that returns the sorted values.",
    ["numpy-sort"],
)

write(
    "recall/review-predict-bisect.yaml",
    f'''id: review-predict-bisect
type: predict_output
rev: 1
prompt: |
  Grade boundaries at 60, 70, 80 and 90, and `bisect.bisect_right` for four scores. What does the program print?
code: |
{block(REVIEW_BISECT)}expected_output: |
{block(REVIEW_BISECT_OUT)}explanation: |
  `bisect_right` returns the index where the score would be inserted to keep the list sorted, after any equal boundary: 59 goes before 60 (index 0), 60 goes after the 60 (index 1), 85 after 80 (index 3), 100 at the end (index 4). That index is how many boundaries the score has reached, which makes it the grade band, found by binary search.
skills: [numpy-sort]
''',
)

mcq(
    "review-mcq-sort-once-or-dict",
    "You must look up 50,000 ids in 2 million records. Sorting the records costs about `n log n` and each binary search about `log n`; a dict costs one pass to build and a step per lookup. Which do you choose, and when would the other be right?",
    [
        "Sort and binary search, always; a dict uses too much memory for 2 million records and is slower to build",
        "A dict for exact lookups; sort when you also need ranges, neighbours or the records in order",
        "A dict, because binary search cannot work on 2 million items",
        "Neither; 50,000 scans of 2 million is only 100 billion steps, which is fine",
    ],
    1,
    "For exact matches the dict wins on both counts: one pass to build against `n log n` to sort, one step per lookup against about 21. The sorted list earns its keep when the question is about order: everything between two ids, the nearest id, the top ten. A hundred billion steps is hours, not fine.",
    ["binary-search", "sorts"],
)

mcq(
    "review-mcq-the-merge-step",
    "Merging two sorted lists of 500 items each into one sorted list of 1,000: how many comparisons at most, and why?",
    [
        "About 250,000: every item in one list is compared with every item in the other, as in a nested loop",
        "About 10: the lists are halved like a binary search, so only a few comparisons are needed",
        "About 1,000: each comparison places one item, and a list that runs out leaves the rest copied",
        "About 500: only the smaller list has to be looked at, and the other follows",
    ],
    2,
    "The merge keeps a finger in each list and compares the two items under the fingers; the smaller one goes to the output and its finger moves. Each comparison places one item, so at most 999 comparisons, and often fewer because the tail of one list is copied once the other is exhausted. A linear merge at each of `log n` levels is what makes merge sort `n log n`.",
    ["sorts"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-search-and-sort-counted/exercise.yaml",
    f'''id: example-search-and-sort-counted
stage: worked_example
rev: 1
title: "Search and sort, counted"
prompt: |
  Two searches and two sorts with their comparisons counted, then what Python and NumPy give you. Press **Run**, then read how each part works.
steps:
  - label: "Binary search"
    lines: "{ln('def binary_search')}-{ln('    return -1')}"
    note: "`lo` and `hi` bracket the indices that could still hold the target. Each loop looks at the middle one: a match returns; a smaller value means the target can only be to the right, so `lo` moves past the middle; a larger one moves `hi` before it. The list must be sorted for that reasoning to hold."
  - label: "A scan, for comparison"
    lines: "{ln('def scan')}-{ln('    return -1', ln('def scan'))}"
    note: "The plain search looks at every item until it finds the target. Both functions count their comparisons in the one-element list they are handed."
  - label: "A million even numbers"
    lines: "{ln('evens = list')}-{ln('    print(name + ')}"
    note: "Finding the last value and ruling out an odd one: the scan makes {thousands(SCAN_COMPARED)} comparisons for the two searches, binary search {BINARY_COMPARED}. Twenty-odd steps for a million items is `log2` at work: a million is about 2 to the 20."
  - label: "Insertion sort"
    lines: "{ln('def insertion_sort')}-{ln('    return result')}"
    note: "The front of the list is kept sorted. Each next item is shifted left past every larger item and dropped where it belongs; the `while` stops at the first item that isn't larger, which on sorted input is immediately."
  - label: "Merge sort"
    lines: "{ln('def merge_sort')}-{ln('    return merged')}"
    note: "Split in half, sort each half by calling the same function (the last topic's recursion), then merge: keep a finger in each sorted half, compare the two items under the fingers, and take the smaller. The merge is one pass over the items; the splitting goes `log2 n` levels deep."
  - label: "Counting the sorts"
    lines: "{ln('for n in (1000, 2000)')}-{ln('2000 already sorted items')}"
    note: "On 1,000 shuffled items, insertion sort makes {thousands(COUNTS[1000]["insertion"])} comparisons and merge sort {thousands(COUNTS[1000]["merge"])}; on 2,000, {thousands(COUNTS[2000]["insertion"])} and {thousands(COUNTS[2000]["merge"])}: doubling multiplied insertion by {INSERTION_RATIO:.1f} (quadratic) and merge by {MERGE_RATIO:.1f} (`n log n`, a bit more than double). On 2,000 items already in order, insertion sort makes just 1,999 comparisons, one per item."
  - label: "sorted, keys and stability"
    lines: "{ln('records = [')}-{ln('print(sorted(records, key=lambda record: (record[0]')}"
    note: "Sorting by city keeps each city's records in the order they came: Oslo's 30 before Oslo's 8, because Python's sort is stable. A tuple key sorts by city and then, within a city, by `-total`, so the larger total comes first. The key function runs once per record."
  - label: "bisect: binary search from the library"
    lines: "{ln('bands = [')}-{ln('is in band')}"
    note: "`bisect_right` finds, by binary search, the index where the score would be inserted after any equal boundary, which is the number of boundaries it has reached: 49 reaches none, 65 reaches two, 95 all four. Banding, bucketing and \\"which threshold\\" questions are this one call."
  - label: "argsort: order one array by another"
    lines: "{ln('names = np.array')}-{ln('print(order, names[order])')}"
    note: "`np.argsort(-scores)` gives the indices that would sort the scores from high to low: 1 (93), 3 (93), 0 (71), 2 (58); `kind=\\"stable\\"` keeps bob before dee on their tie. Indexing `names` with those indices lists the names in score order. Top-k predictions and rankings are read off a score vector exactly like this."
''',
)
write("exercises/example-search-and-sort-counted/solution.py", EXAMPLE)
write(
    "exercises/example-search-and-sort-counted/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the search counts, the sort counts, the keyed sorts, the bands and the argsort order."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-merge-two-sorted-lists/exercise.yaml",
    f'''id: fill-merge-two-sorted-lists
stage: fill_in
rev: 1
title: "Merge two sorted lists"
prompt: |
  `merge(left, right)` should combine two sorted lists into one sorted list in a single pass: compare the items under the two fingers `i` and `j`, take the smaller, and when one list runs out, copy the rest of the other. Replace each `...` so the program prints:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "The item under the right finger is `right[j]`."
  - "Whatever is left of `left` from index `i` on is `left[i:]`, and it is already sorted."
skills: [sorts]
''',
)
write("exercises/fill-merge-two-sorted-lists/starter.py", FILL_STARTER)
write("exercises/fill-merge-two-sorted-lists/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-merge-two-sorted-lists/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the three merged lists."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_leftovers_on_either_side():
    """Whichever list runs out first, the rest of the other is kept, and two empty lists merge to nothing."""
    merge = function("merge")
    assert merge([1, 2, 3], [0]) == [0, 1, 2, 3]
    assert merge([5], [1, 2, 3]) == [1, 2, 3, 5]
    assert merge([], []) == []
''',
)
write("exercises/fill-merge-two-sorted-lists/wrong/drops-the-right-tail.py", FILL_WRONG)
write(
    "exercises/fill-merge-two-sorted-lists/wrong/typed-in.py",
    "def merge(left, right):\n    return [1, 2, 3, 4, 9, 10, 11]\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-binary-search/exercise.yaml",
    f'''id: write-binary-search
stage: write
rev: 1
title: "Binary search"
prompt: |
  Write `binary_search(items, target)`, which returns the index of `target` in a sorted list, or `-1` if it isn't there, by halving: keep `lo` and `hi` as the first and last index that could still hold the target, look at the middle, and move `lo` or `hi` past it. Then print it for these calls:

  ```python
  primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
  print(binary_search(primes, 2), binary_search(primes, 29), binary_search(primes, 13))
  print(binary_search(primes, 4), binary_search([], 1))
  ```

  ```
{block(WRITE_OUT)}  ```

  The checks count comparisons: on 100,000 items a binary search makes a few dozen, a scan up to 100,000.
hints:
  - "`mid = (lo + hi) // 2`; the loop runs while `lo <= hi`, so a single remaining candidate is still checked."
  - "After `items[mid] < target`, set `lo = mid + 1`; otherwise `hi = mid - 1`."
skills: [binary-search]
''',
)
write("exercises/write-binary-search/starter.py", "")
write("exercises/write-binary-search/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-binary-search/test_exercise.py",
    f'''from checks import function, run
{TRACKED}

def test_the_output():
    """Prints the five results."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_a_hundred_thousand_items():
    """The last of 100,000 items is found, and a missing one reported, within 80 comparisons in all."""
    binary_search = function("binary_search")
    items = tracked(range(0, 200_000, 2))
    Tracked.compared = 0
    assert binary_search(items, Tracked(199_998)) == 99_999
    assert binary_search(items, Tracked(199_999)) == -1
    assert Tracked.compared <= 80, f"{{Tracked.compared}} comparisons: halve, don't scan"
''',
)
write("exercises/write-binary-search/wrong/scans.py", WRITE_SCAN)
write("exercises/write-binary-search/wrong/stops-one-early.py", WRITE_OFF_BY_ONE)
write(
    "exercises/write-binary-search/wrong/typed-in.py",
    "def binary_search(items, target):\n    return -1\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-sort-and-search/exercise.yaml",
    f'''id: build-sort-and-search
stage: build
rev: 1
title: "Sort and search"
prompt: |
  Starting from a blank editor, write four functions:

  - `insertion_sort(items)`: a new sorted list by insertion sort: keep a sorted front, and shift each next item left past the items larger than it, **stopping at the first that isn't**, so that input already in order costs one comparison per item.
  - `merge_sort(items)`: a new sorted list by merge sort: split in half, sort each half the same way, merge the sorted halves in one pass.
  - `binary_search(items, target)`: the index of `target` in a sorted list, or `-1`, by halving.
  - `top_k_by(records, field, k)`: the `k` records (dicts) with the largest value of `field`, largest first, with ties in their original order; `sorted` with a key does it.

  Then print:

  ```python
  print(insertion_sort([5, 2, 9, 1, 5, 6]), merge_sort([5, 2, 9, 1, 5, 6]))
  print(binary_search([1, 3, 5, 7, 9], 7), binary_search([1, 3, 5, 7, 9], 4))
  scores = [{{"name": "ann", "score": 71}}, {{"name": "bob", "score": 93}}, {{"name": "cy", "score": 58}}, {{"name": "dee", "score": 93}}]
  print([record["name"] for record in top_k_by(scores, "score", 3)])
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks count comparisons: insertion sort on 3,000 items already in order must make fewer than 6,000; merge sort on 3,000 shuffled items fewer than 60,000 (insertion sort would make about 2 million); binary search on 100,000 items fewer than 80.
skills: [sorts, binary-search, keys]
''',
)
write("exercises/build-sort-and-search/starter.py", "")
write("exercises/build-sort-and-search/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-sort-and-search/test_exercise.py",
    f'''import random

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).
{TRACKED}

def test_the_output():
    """Prints the three lines."""
    assert run() == {BUILD_OUT!r}


def test_insertion_sort_on_sorted_input():
    """3,000 items already in order are sorted with fewer than 6,000 comparisons, and a shuffled list comes out sorted."""
    insertion_sort = function("insertion_sort")
    Tracked.compared = 0
    assert values(insertion_sort(tracked(range(3000)))) == list(range(3000))
    assert Tracked.compared < 6000
    data = list(range(200))
    random.Random(3).shuffle(data)
    assert values(insertion_sort(tracked(data))) == list(range(200))


def test_merge_sort_scales():
    """3,000 shuffled items are sorted with fewer than 60,000 comparisons."""
    merge_sort = function("merge_sort")
    data = list(range(3000))
    random.Random(4).shuffle(data)
    Tracked.compared = 0
    assert values(merge_sort(tracked(data))) == list(range(3000))
    assert Tracked.compared < 60_000


def test_binary_search_halves():
    """The last of 100,000 items is found, and a missing one reported, within 80 comparisons."""
    binary_search = function("binary_search")
    items = tracked(range(0, 200_000, 2))
    Tracked.compared = 0
    assert binary_search(items, Tracked(199_998)) == 99_999 and binary_search(items, Tracked(199_999)) == -1
    assert Tracked.compared <= 80


def test_top_k_by():
    """Ties keep their original order, and k larger than the list returns everything."""
    top_k_by = function("top_k_by")
    records = [{{"n": "a", "v": 1}}, {{"n": "b", "v": 3}}, {{"n": "c", "v": 3}}, {{"n": "d", "v": 2}}]
    assert [r["n"] for r in top_k_by(records, "v", 2)] == ["b", "c"]
    assert [r["n"] for r in top_k_by(records, "v", 10)] == ["b", "c", "d", "a"]
''',
)
write("exercises/build-sort-and-search/wrong/insertion-from-the-left.py", BUILD_INSERTION_FROM_LEFT)
write("exercises/build-sort-and-search/wrong/merge-sort-is-insertion.py", BUILD_MERGE_IS_INSERTION)
write("exercises/build-sort-and-search/wrong/search-scans.py", BUILD_SCAN_SEARCH)
write("exercises/build-sort-and-search/wrong/top-k-ascending.py", BUILD_TOP_K_ASCENDING)
write(
    "exercises/build-sort-and-search/wrong/typed-in.py",
    "def insertion_sort(items):\n    return [1, 2, 5, 5, 6, 9]\n\n\ndef merge_sort(items):\n    return [1, 2, 5, 5, 6, 9]\n\n\ndef binary_search(items, target):\n    return 3\n\n\ndef top_k_by(records, field, k):\n    return records[:k]\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-search-that-misses/exercise.yaml",
    f'''id: debug-a-search-that-misses
stage: debug
rev: 1
title: "A search that misses"
prompt: |
  Ten sensor readings are sorted, and four targets are searched for by binary search. The program should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: 2 is reported at index 4 and 30 is not found at all, because the search runs on the **unsorted** `readings`; binary search only works on `ordered`. Fix that, and 2 and 88 are still missed: the loop stops as soon as `lo == hi`, with one candidate left unchecked. It must run while `lo <= hi`.
skills: [binary-search]
''',
)
write("exercises/debug-a-search-that-misses/starter.py", DEBUG_STARTER)
write("exercises/debug-a-search-that-misses/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-search-that-misses/test_exercise.py",
    f'''from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the sorted readings and the four searches."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_edges():
    """The last element and a single-element list are found; the first element of two is found."""
    binary_search = function("binary_search")
    assert binary_search(list(range(0, 1000, 2)), 998) == 499
    assert binary_search([5], 5) == 0 and binary_search([5, 6], 5) == 0
''',
)
write("exercises/debug-a-search-that-misses/wrong/still-unsorted.py", DEBUG_STILL_UNSORTED)
write("exercises/debug-a-search-that-misses/wrong/still-stops-early.py", DEBUG_STILL_LOOP)
write(
    "exercises/debug-a-search-that-misses/wrong/typed-in.py",
    "def binary_search(items, target):\n    return -1\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-binary-search/exercise.yaml",
    f'''id: review-binary-search
stage: review_code
rev: 1
title: "Binary search, from memory"
prompt: |
  Write `binary_search(items, target)`, the index of `target` in a sorted list or `-1`, by halving, and print it for the ten primes `[2, 3, 5, 7, 11, 13, 17, 19, 23, 29]` with targets 2, 29 and 13 on one line, then 4 and an empty list's 1 on the next:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [binary-search]
''',
)
write("exercises/review-binary-search/starter.py", "")
write("exercises/review-binary-search/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-binary-search/test_exercise.py",
    f'''from checks import function, run
{TRACKED}

def test_the_output():
    """Prints the five results."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_halves():
    """100,000 items are searched within 80 comparisons."""
    binary_search = function("binary_search")
    items = tracked(range(0, 200_000, 2))
    Tracked.compared = 0
    assert binary_search(items, Tracked(199_998)) == 99_999 and binary_search(items, Tracked(3)) == -1
    assert Tracked.compared <= 80
''',
)
write("exercises/review-binary-search/wrong/scans.py", WRITE_SCAN)
write(
    "exercises/review-binary-search/wrong/typed-in.py",
    "def binary_search(items, target):\n    return 0\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.dsa.sorting-and-searching written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
