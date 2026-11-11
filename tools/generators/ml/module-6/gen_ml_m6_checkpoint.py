"""Writes ml.m6.checkpoint, "Checkpoint 6: the algorithms behind a pipeline",
which closes the ML track's Module 6. Run from the repository root under uv
(python -m uv run python <this file>), so every program's expected output is
captured from CPython rather than typed in. The hidden tests count comparisons
on wrapped values, so both runtimes agree. Files are written as bytes with LF
endings."""

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.m6.checkpoint")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str) -> str:
    result = subprocess.run([sys.executable, "-c", program], capture_output=True, text=True, check=True)
    return result.stdout.replace("\r\n", "\n")


def block(text: str, indent: str = "  ") -> str:
    return "".join(indent + line + "\n" for line in text.rstrip("\n").splitlines())


# --- the toolkit -----------------------------------------------------------------------------

FUNCTIONS = '''def dedupe(records, key):
    """The first record for each value of the key field, in order: one pass with a set."""
    seen = set()
    kept = []
    for record in records:
        if record[key] not in seen:
            seen.add(record[key])
            kept.append(record)
    return kept


def top_k(records, field, k):
    """The k records with the largest field value, largest first, through a heap of at most k entries; ties keep the earlier record first."""
    heap = []
    for i, record in enumerate(records):
        heapq.heappush(heap, (record[field], -i, record))
        if len(heap) > k:
            heapq.heappop(heap)
    return [record for value, i, record in sorted(heap, key=lambda entry: (entry[0], entry[1]), reverse=True)]


def join(left, right, key):
    """Every left record merged with every right record sharing its key value, in left order: a hash join."""
    by_key = {}
    for record in right:
        by_key.setdefault(record[key], []).append(record)
    merged = []
    for record in left:
        for match in by_key.get(record[key], []):
            merged.append({**record, **match})
    return merged


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


def closest_name(query, names):
    """The name with the smallest edit distance to the query, and that distance; ties keep the first."""
    best, best_distance = None, None
    for name in names:
        distance = edit_distance(query, name)
        if best_distance is None or distance < best_distance:
            best, best_distance = name, distance
    return best, best_distance


def schedule(steps):
    """An order that runs every step after the steps it depends on (steps maps each step to its dependencies), taking ready steps in the order they became ready; ValueError if the steps form a cycle."""
    remaining = {step: len(deps) for step, deps in steps.items()}
    dependents = {step: [] for step in steps}
    for step, deps in steps.items():
        for dep in deps:
            dependents[dep].append(step)
    ready = deque(step for step in steps if remaining[step] == 0)
    order = []
    while ready:
        step = ready.popleft()
        order.append(step)
        for dependent in dependents[step]:
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                ready.append(dependent)
    if len(order) < len(steps):
        raise ValueError("the steps depend on each other in a cycle")
    return order
'''
HEADER = "import heapq\nfrom collections import deque\n\n\n"

DATASETS = {
    "main": '''events = [
    {"id": 7, "user": "ann", "spend": 40},
    {"id": 3, "user": "bob", "spend": 15},
    {"id": 7, "user": "ann", "spend": 40},
    {"id": 9, "user": "cy", "spend": 70},
    {"id": 3, "user": "bob", "spend": 15},
    {"id": 12, "user": "dee", "spend": 70},
    {"id": 15, "user": "ann", "spend": 5},
]
users = [{"user": "ann", "city": "Oslo"}, {"user": "bob", "city": "Lima"}, {"user": "cy", "city": "Pune"}]
unique = dedupe(events, "id")
print(len(events), "events,", len(unique), "distinct")
print([event["id"] for event in top_k(unique, "spend", 3)])
print([(row["id"], row["city"]) for row in join(unique, users, "user")])
print(closest_name("Pnue", ["Oslo", "Lima", "Pune"]))
steps = {"load": [], "clean": ["load"], "features": ["clean", "join"], "join": ["load"], "train": ["features"], "report": ["train", "clean"]}
print(schedule(steps))
''',
    "logs": '''requests = [
    {"request": "r1", "service": "search", "ms": 120},
    {"request": "r2", "service": "payment", "ms": 480},
    {"request": "r1", "service": "search", "ms": 120},
    {"request": "r3", "service": "auth", "ms": 95},
    {"request": "r4", "service": "payment", "ms": 480},
    {"request": "r2", "service": "payment", "ms": 480},
    {"request": "r5", "service": "search", "ms": 210},
    {"request": "r6", "service": "billing", "ms": 30},
]
services = [{"service": "search", "team": "discovery"}, {"service": "payment", "team": "money"}, {"service": "auth", "team": "identity"}]
unique = dedupe(requests, "request")
print(len(requests), "lines,", len(unique), "requests")
print([row["request"] for row in top_k(unique, "ms", 3)])
print([(row["request"], row["team"]) for row in join(unique, services, "service")])
print(closest_name("paymnet", ["search", "payment", "auth"]))
steps = {"build": [], "test": ["build"], "scan": ["build"], "stage": ["test", "scan"], "smoke": ["stage"], "release": ["smoke", "scan"]}
print(schedule(steps))
''',
    "catalog": '''products = [
    {"sku": "A1", "supplier": "north", "price": 25},
    {"sku": "B2", "supplier": "east", "price": 60},
    {"sku": "A1", "supplier": "north", "price": 25},
    {"sku": "C3", "supplier": "north", "price": 60},
    {"sku": "D4", "supplier": "west", "price": 12},
    {"sku": "B2", "supplier": "east", "price": 60},
    {"sku": "E5", "supplier": "east", "price": 45},
]
suppliers = [{"supplier": "north", "country": "NO"}, {"supplier": "east", "country": "EE"}]
unique = dedupe(products, "sku")
print(len(products), "rows,", len(unique), "products")
print([row["sku"] for row in top_k(unique, "price", 3)])
print([(row["sku"], row["country"]) for row in join(unique, suppliers, "supplier")])
print(closest_name("nroth", ["north", "east", "west"]))
steps = {"download": [], "parse": ["download"], "validate": ["parse"], "prices": ["parse"], "merge": ["validate", "prices"], "publish": ["merge"]}
print(schedule(steps))
''',
}


def build_solution(key: str) -> str:
    return HEADER + FUNCTIONS + "\n\n" + DATASETS[key]


EXPECTED = {key: out(build_solution(key)) for key in DATASETS}
for key, text in EXPECTED.items():
    print(key + ":\n" + text)
assert EXPECTED["main"] == (
    "7 events, 5 distinct\n"
    "[9, 12, 7]\n"
    "[(7, 'Oslo'), (3, 'Lima'), (9, 'Pune'), (15, 'Oslo')]\n"
    "('Pune', 2)\n"
    "['load', 'clean', 'join', 'features', 'train', 'report']\n"
), EXPECTED["main"]
assert EXPECTED["logs"].splitlines()[0] == "8 lines, 6 requests" and EXPECTED["logs"].splitlines()[3] == "('payment', 2)", EXPECTED["logs"]
assert EXPECTED["catalog"].splitlines()[0] == "7 rows, 5 products" and EXPECTED["catalog"].splitlines()[3] == "('north', 2)", EXPECTED["catalog"]

TRACKED = '''

class Tracked:
    """A value that counts how often it is compared, whichever comparison is used; hashing is free."""

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


class Ordered:
    """A value that counts only its ordering comparisons: tuples in a heap test equality first, and that test is free here."""

    compared = 0

    def __init__(self, value):
        self.value = value

    def _count(self):
        Ordered.compared += 1

    def __eq__(self, other):
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


def ordered(values):
    return [Ordered(v) for v in values]
'''

# The top-k budget sits between the heap's count and a full sort's, measured here.
PROBE = HEADER + FUNCTIONS + "\nimport random\n" + TRACKED + '''

rng = random.Random(7)
records = [{"v": value} for value in ordered(rng.randint(1, 10**9) for _ in range(20_000))]
Ordered.compared = 0
top_k(records, "v", 5)
heap_count = Ordered.compared
Ordered.compared = 0
sorted(records, key=lambda record: record["v"], reverse=True)[:5]
print(heap_count, Ordered.compared)
'''
HEAP_COUNT, SORT_COUNT = (int(v) for v in out(PROBE).split())
print("top-k probe: heap", HEAP_COUNT, "sort", SORT_COUNT)
TOP_K_BUDGET = (HEAP_COUNT + SORT_COUNT) // 2
assert HEAP_COUNT < 0.75 * TOP_K_BUDGET and SORT_COUNT > 1.33 * TOP_K_BUDGET, (HEAP_COUNT, SORT_COUNT)

WRONG = {
    "dedupe-with-a-list": ("    seen = set()\n    kept = []\n    for record in records:\n        if record[key] not in seen:\n            seen.add(record[key])", "    seen = []\n    kept = []\n    for record in records:\n        if record[key] not in seen:\n            seen.append(record[key])"),
    "top-k-by-sorting": (
        '''    heap = []
    for i, record in enumerate(records):
        heapq.heappush(heap, (record[field], -i, record))
        if len(heap) > k:
            heapq.heappop(heap)
    return [record for value, i, record in sorted(heap, key=lambda entry: (entry[0], entry[1]), reverse=True)]''',
        "    return sorted(records, key=lambda record: record[field], reverse=True)[:k]",
    ),
    "join-by-scanning": (
        '''    by_key = {}
    for record in right:
        by_key.setdefault(record[key], []).append(record)
    merged = []
    for record in left:
        for match in by_key.get(record[key], []):
            merged.append({**record, **match})
    return merged''',
        '''    merged = []
    for record in left:
        for match in right:
            if match[key] == record[key]:
                merged.append({**record, **match})
    return merged''',
    ),
    "schedule-ignores-cycles": ("    if len(order) < len(steps):\n        raise ValueError(\"the steps depend on each other in a cycle\")\n    return order", "    return order"),
}
for name, (old, new) in WRONG.items():
    assert old in FUNCTIONS, name
    assert out(build_solution("main").replace(old, new)) == EXPECTED["main"], name + " should print the right answer and fail a count or a cycle"

# --- the debug: three bugs ------------------------------------------------------------------------

BUG_LIST = WRONG["dedupe-with-a-list"]
BUG_LIFO = ("        step = ready.popleft()", "        step = ready.pop()")
BUG_ROWS = ("    for i in range(1, len(a) + 1):\n        for j in range(1, len(b) + 1):", "    for i in range(len(a), 0, -1):\n        for j in range(1, len(b) + 1):")
DEBUG_SOLUTION = build_solution("main")
for old, new in (BUG_LIST, BUG_LIFO, BUG_ROWS):
    assert old in DEBUG_SOLUTION, old
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_LIST).replace(*BUG_LIFO).replace(*BUG_ROWS)
DEBUG_STILL_LIST = DEBUG_SOLUTION.replace(*BUG_LIST)
DEBUG_STILL_LIFO = DEBUG_SOLUTION.replace(*BUG_LIFO)
DEBUG_STILL_ROWS = DEBUG_SOLUTION.replace(*BUG_ROWS)
STARTER_OUT = out(DEBUG_STARTER)
LIFO_OUT = out(DEBUG_STILL_LIFO)
ROWS_OUT = out(DEBUG_STILL_ROWS)
print("starter:\n" + STARTER_OUT + "lifo only:\n" + LIFO_OUT + "rows only:\n" + ROWS_OUT)
assert out(DEBUG_STILL_LIST) == EXPECTED["main"], "the list bug prints the right answer and only the count catches it"
assert LIFO_OUT.splitlines()[4] == "['load', 'join', 'clean', 'features', 'train', 'report']", LIFO_OUT
assert ROWS_OUT.splitlines()[3] != "('Pune', 2)", ROWS_OUT
assert STARTER_OUT != EXPECTED["main"]
LIFO_ORDER = LIFO_OUT.splitlines()[4]
ROWS_CLOSEST = ROWS_OUT.splitlines()[3]

# --- the solved sibling: the toolkit on a tiny dataset ------------------------------------------

EXAMPLE = HEADER + FUNCTIONS + '''

readings = [
    {"sensor": "s1", "value": 9},
    {"sensor": "s2", "value": 4},
    {"sensor": "s1", "value": 9},
    {"sensor": "s3", "value": 7},
]
places = [{"sensor": "s1", "room": "lab"}, {"sensor": "s3", "room": "hall"}]
unique = dedupe(readings, "sensor")
print(len(readings), "readings,", len(unique), "sensors")
print([row["sensor"] for row in top_k(unique, "value", 2)])
print([(row["sensor"], row["room"]) for row in join(unique, places, "sensor")])
print(edit_distance("kitten", "sitting"), closest_name("hal", ["lab", "hall"]))
print(schedule({"read": [], "calibrate": ["read"], "store": ["calibrate"], "plot": ["calibrate"]}))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
assert EXAMPLE_OUT == "4 readings, 3 sensors\n['s1', 's3']\n[('s1', 'lab'), ('s3', 'hall')]\n3 ('hall', 1)\n['read', 'calibrate', 'store', 'plot']\n", EXAMPLE_OUT
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- the steps -----------------------------------------------------------------------------------

STEP_DATA = '''records = [{"id": 7, "spend": 40}, {"id": 3, "spend": 15}, {"id": 7, "spend": 40}, {"id": 9, "spend": 70}, {"id": 3, "spend": 15}]
'''

STEP1_HEAD = '''def dedupe(records, key):
    """The first record for each value of the key field, in order."""
    seen = SET
    kept = []
    for record in records:
        if record[key] not in seen:
            seen.ADD(record[key])
            kept.append(record)
    return kept


''' + STEP_DATA + '''print([record["id"] for record in dedupe(records, "id")])
'''
STEP1_SOLUTION = STEP1_HEAD.replace("seen = SET", "seen = set()").replace("seen.ADD(", "seen.add(")
STEP1_STARTER = STEP1_HEAD.replace("seen = SET", "seen = ...").replace("seen.ADD(", "seen....(")
STEP1_OUT = out(STEP1_SOLUTION)
assert STEP1_OUT == "[7, 3, 9]\n", STEP1_OUT
assert "..." in STEP1_STARTER

STEP2_HEAD = '''import heapq


def top_k(records, field, k):
    """The k records with the largest field value, largest first, through a heap of at most k entries."""
    heap = []
    for i, record in enumerate(records):
        heapq.heappush(heap, (record[field], -i, record))
        if len(heap) > K:
            heapq.POP(heap)
    return [record for value, i, record in sorted(heap, key=lambda entry: (entry[0], entry[1]), reverse=True)]


''' + STEP_DATA + '''print([record["id"] for record in top_k(records, "spend", 2)])
print([record["id"] for record in top_k(records, "spend", 10)])
'''
STEP2_SOLUTION = STEP2_HEAD.replace("len(heap) > K", "len(heap) > k").replace("heapq.POP(", "heapq.heappop(")
STEP2_STARTER = STEP2_HEAD.replace("len(heap) > K", "len(heap) > ...").replace("heapq.POP(", "heapq....(")
STEP2_OUT = out(STEP2_SOLUTION)
assert STEP2_OUT == "[9, 7]\n[9, 7, 7, 3, 3]\n", STEP2_OUT

STEP3_HEAD = '''def join(left, right, key):
    """Every left record merged with every right record sharing its key value, in left order."""
    by_key = {}
    for record in right:
        by_key.setdefault(record[KEY], []).append(record)
    merged = []
    for record in left:
        for match in by_key.get(record[key], DEFAULT):
            merged.append({**record, **match})
    return merged


users = [{"user": "ann", "city": "Oslo"}, {"user": "bob", "city": "Lima"}]
events = [{"id": 1, "user": "ann"}, {"id": 2, "user": "cy"}, {"id": 3, "user": "bob"}, {"id": 4, "user": "ann"}]
print([(row["id"], row["city"]) for row in join(events, users, "user")])
'''
STEP3_SOLUTION = STEP3_HEAD.replace("record[KEY]", "record[key]").replace("DEFAULT)", "[])")
STEP3_STARTER = STEP3_HEAD.replace("record[KEY]", "record[...]").replace("DEFAULT)", "...)")
STEP3_OUT = out(STEP3_SOLUTION)
assert STEP3_OUT == "[(1, 'Oslo'), (3, 'Lima'), (4, 'Oslo')]\n", STEP3_OUT

STEP4_HEAD = '''from collections import deque


def schedule(steps):
    """An order that runs every step after its dependencies; ValueError on a cycle."""
    remaining = {step: len(deps) for step, deps in steps.items()}
    dependents = {step: [] for step in steps}
    for step, deps in steps.items():
        for dep in deps:
            dependents[dep].append(step)
    ready = deque(step for step in steps if remaining[step] == 0)
    order = []
    while ready:
        step = ready.popleft()
        order.append(step)
        for dependent in dependents[step]:
            remaining[dependent] -= ONE
            if remaining[dependent] == ZERO:
                ready.append(dependent)
    if len(order) < len(steps):
        raise ValueError("the steps depend on each other in a cycle")
    return order


print(schedule({"load": [], "clean": ["load"], "features": ["clean", "join"], "join": ["load"], "train": ["features"]}))
try:
    schedule({"a": ["b"], "b": ["a"]})
except ValueError as error:
    print(error)
'''
STEP4_SOLUTION = STEP4_HEAD.replace("-= ONE", "-= 1").replace("== ZERO", "== 0")
STEP4_STARTER = STEP4_HEAD.replace("-= ONE", "-= ...").replace("== ZERO", "== ...")
STEP4_OUT = out(STEP4_SOLUTION)
assert STEP4_OUT == "['load', 'clean', 'join', 'features', 'train']\nthe steps depend on each other in a cycle\n", STEP4_OUT

# =====================================================================================
# the build and its fresh versions
# =====================================================================================

TEST_SKILLS = '''# Every test names the module skills it checks (ADR-0012), so a failed test
# says which topics to revisit.
test_skills:
  test_the_output: [ml.dsa.arrays-and-hashing/patterns, ml.dsa.graphs/topo, ml.dsa.dynamic-programming/edit-distance]
  test_dedupe_scales: [ml.dsa.arrays-and-hashing/replace, ml.dsa.complexity/choose]
  test_top_k_scales: [ml.dsa.trees-and-heaps/heap, ml.dsa.complexity/choose]
  test_join_scales: [ml.dsa.arrays-and-hashing/patterns, ml.dsa.arrays-and-hashing/hashing]
  test_closest_name: [ml.dsa.dynamic-programming/edit-distance]
  test_schedule: [ml.dsa.graphs/topo, ml.dsa.stacks-queues-recursion/stack-queue]
'''


def build_tests(key: str) -> str:
    return f'''import random

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).
{TRACKED}

def test_the_output():
    """Prints the five lines."""
    assert run() == {EXPECTED[key]!r}


def test_dedupe_scales():
    """3,000 records with 1,500 distinct keys dedupe to 1,500, first-seen first, within 30,000 comparisons (a list for seen makes about 2 million)."""
    dedupe = function("dedupe")
    records = [{{"key": key, "n": i}} for i, key in enumerate(tracked(i % 1500 for i in range(3000)))]
    Tracked.compared = 0
    kept = dedupe(records, "key")
    assert [record["n"] for record in kept] == list(range(1500))
    assert Tracked.compared < 30_000


def test_top_k_scales():
    """The 5 largest of 20,000 records are right, found within {TOP_K_BUDGET:,} comparisons (sorting everything makes about {SORT_COUNT:,})."""
    top_k = function("top_k")
    rng = random.Random(7)
    values = [rng.randint(1, 10**9) for _ in range(20_000)]
    records = [{{"v": value}} for value in ordered(values)]
    Ordered.compared = 0
    result = top_k(records, "v", 5)
    assert [record["v"].value for record in result] == sorted(values, reverse=True)[:5]
    assert Ordered.compared < {TOP_K_BUDGET}


def test_join_scales():
    """1,000 left records joined with 2,000 right records, each key matching twice, give 2,000 rows in left order within 60,000 comparisons (a scan makes 2 million)."""
    join = function("join")
    keys = tracked(range(1000))
    left = [{{"k": key, "left": i}} for i, key in enumerate(keys)]
    right = [{{"k": keys[i % 1000], "right": i}} for i in range(2000)]
    Tracked.compared = 0
    rows = join(left, right, "k")
    assert len(rows) == 2000 and rows[0]["left"] == 0 and rows[0]["right"] == 0 and rows[1]["right"] == 1000
    assert Tracked.compared < 60_000


def test_closest_name():
    """kitten is closest to mitten (1 edit), a tie keeps the first name, and an exact match is distance 0."""
    closest_name = function("closest_name")
    assert closest_name("kitten", ["sitting", "mitten", "bitten"]) == ("mitten", 1)
    assert closest_name("ab", ["ac", "cb"]) == ("ac", 1)
    assert closest_name("same", ["other", "same"]) == ("same", 0)


def test_schedule():
    """A chain of 300 steps runs in chain order, a diamond respects its dependencies, and a cycle raises ValueError."""
    schedule = function("schedule")
    chain = {{"s0": []}}
    for i in range(1, 300):
        chain[f"s{{i}}"] = [f"s{{i - 1}}"]
    assert schedule(chain) == [f"s{{i}}" for i in range(300)]
    order = schedule({{"d": ["b", "c"], "a": [], "b": ["a"], "c": ["a"]}})
    assert order.index("a") < order.index("b") < order.index("d") and order.index("a") < order.index("c") < order.index("d")
    try:
        schedule({{"a": ["b"], "b": ["c"], "c": ["a"]}})
    except ValueError:
        pass
    else:
        raise AssertionError("a cycle should raise ValueError")
'''


def write_build(folder: str, title: str, opening: str, key: str, data_name: str, what: str) -> None:
    data = DATASETS[key]
    prompt = f'''  {opening}

  **Write five functions**, each at the right order of growth:

  - `dedupe(records, key)`: the first record for each value of the `key` field, in order; one pass with a set.
  - `top_k(records, field, k)`: the `k` records with the largest `field` value, largest first, through a heap that never holds more than `k` entries; ties keep the earlier record first.
  - `join(left, right, key)`: every left record merged with every right record that has the same `key` value (`{{**left_record, **right_record}}`), in left order; index the right side in a dict first (a hash join).
  - `closest_name(query, names)`: the name with the smallest edit distance to `query`, and that distance, as a tuple; ties keep the first name. You will need `edit_distance(a, b)` by the table.
  - `schedule(steps)`: `steps` maps each step to the list of steps it depends on; return an order that runs every step after its dependencies, taking ready steps in the order they became ready (a queue), and raise `ValueError` if the steps form a cycle.

  **Then run them on {data_name}:**

  ```python
{block(data)}  ```

  ```
{block(EXPECTED[key])}  ```

  {what}

  The checks count how often your code compares two keys or values: 3,000 records to dedupe within 30,000 comparisons, the top 5 of 20,000 within {TOP_K_BUDGET:,}, a join of 1,000 with 2,000 within 60,000; a chain of 300 steps to schedule, a diamond and a cycle; and names at known distances.
'''
    write(
        f"exercises/{folder}/exercise.yaml",
        f'''id: {folder}
stage: build
rev: 1
title: "{title}"
prompt: |
{prompt}{TEST_SKILLS}''',
    )
    write(f"exercises/{folder}/starter.py", "")
    write(f"exercises/{folder}/solution.py", build_solution(key))
    write(f"exercises/{folder}/test_exercise.py", build_tests(key))
    for name, (old, new) in WRONG.items():
        write(f"exercises/{folder}/wrong/{name}.py", build_solution(key).replace(old, new))
    write(
        f"exercises/{folder}/wrong/typed-in.py",
        "def dedupe(records, key):\n    return records\n\n\ndef top_k(records, field, k):\n    return records[:k]\n\n\ndef join(left, right, key):\n    return []\n\n\ndef closest_name(query, names):\n    return (names[0], 0)\n\n\ndef schedule(steps):\n    return list(steps)\n\n\n"
        + "".join(f"print({line!r})\n" for line in EXPECTED[key].splitlines()),
    )


write_build(
    "build-a-pipeline-toolkit",
    "The algorithms behind a pipeline",
    "Starting from a blank editor, build the pieces a small data pipeline is made of, each with the structure that makes it fast: a set, a heap, a dict, a table and a queue.",
    "main",
    "a week of shop events, some logged twice, and the users they belong to",
    "Seven events with two duplicates leave five; the top three by spend put the two 70s first with the earlier one ahead; the join drops dee, who has no user record; `Pnue` is two edits from `Pune`; and the pipeline runs load, then clean and join as they become ready, then features, train and report.",
)
write_build(
    "build-a-pipeline-toolkit-logs",
    "The algorithms behind a pipeline: request logs",
    "Starting from a blank editor, build the same five pieces for a different pipeline: request logs with retried lines, the slowest requests, the teams that own each service, a misspelled service name, and a deployment's steps.",
    "logs",
    "a morning of request logs, some lines written twice by retries, and the teams that own each service",
    "Eight lines with two retries leave six requests; the top three by milliseconds put the two 480s first with the earlier ahead; the join drops billing, which no team owns; `paymnet` is two edits from `payment`; and the deployment builds, then tests and scans, then stages, smokes and releases.",
)
write_build(
    "build-a-pipeline-toolkit-catalog",
    "The algorithms behind a pipeline: a product catalogue",
    "Starting from a blank editor, build the same five pieces for a catalogue import: product rows with duplicates, the dearest products, the suppliers' countries, a misspelled supplier, and an import's steps.",
    "catalog",
    "a catalogue export with repeated rows, and the suppliers' countries",
    "Seven rows with two duplicates leave five products; the top three by price put the two 60s first with the earlier ahead; the join drops the products whose supplier has no country record; `nroth` is two edits from `north`; and the import downloads, parses, validates and prices, then merges and publishes.",
)

# =====================================================================================
# the debug
# =====================================================================================

write(
    "exercises/debug-a-slow-pipeline/exercise.yaml",
    f'''id: debug-a-slow-pipeline
stage: debug
rev: 1
title: "Three bugs in a pipeline"
prompt: |
  This is the checkpoint's toolkit on its data, and it should print:

  ```
{block(EXPECTED["main"])}  ```

  It has three bugs, in three different functions. Run it:

  1. **The schedule runs `join` before `clean`:** `{LIFO_ORDER}`. The scheduler takes ready steps from the **back** of its deque with `pop()`, which makes it a stack; the steps that became ready first must run first, which is `popleft()`.
  2. **The closest name is wrong:** `{ROWS_CLOSEST}` instead of `('Pune', 2)`. The edit-distance table is filled from the **bottom row up**, so every cell reads neighbours that haven't been computed yet. A table has to be filled in an order where each cell's three neighbours (above, left, diagonal) are already done: row by row from the top, left to right.
  3. **The dedupe is quadratic and prints the right answer anyway:** `seen` is a list, so `record[key] not in seen` scans it every time. The checks count the comparisons (fewer than 30,000 on 3,000 records; the list makes about 2 million), and only a set passes.
# Every test names the module skills it checks (ADR-0012), so a failed test
# says which topics to revisit.
test_skills:
  test_the_output: [ml.dsa.graphs/topo, ml.dsa.dynamic-programming/edit-distance]
  test_dedupe_scales: [ml.dsa.arrays-and-hashing/replace, ml.dsa.complexity/choose]
  test_schedule_is_a_queue: [ml.dsa.stacks-queues-recursion/stack-queue, ml.dsa.graphs/topo]
  test_edit_distance: [ml.dsa.dynamic-programming/edit-distance]
''',
)
write("exercises/debug-a-slow-pipeline/starter.py", DEBUG_STARTER)
write("exercises/debug-a-slow-pipeline/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-slow-pipeline/test_exercise.py",
    f'''from checks import function, run

EXPECTED = {EXPECTED["main"]!r}
{TRACKED}

def test_the_output():
    """Prints the five lines, with the schedule in queue order and Pune two edits away."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_dedupe_scales():
    """3,000 records with 1,500 distinct keys dedupe within 30,000 comparisons: seen must be a set."""
    dedupe = function("dedupe")
    records = [{{"key": key, "n": i}} for i, key in enumerate(tracked(i % 1500 for i in range(3000)))]
    Tracked.compared = 0
    assert len(dedupe(records, "key")) == 1500
    assert Tracked.compared < 30_000, f"{{Tracked.compared}} comparisons: seen must be a set"


def test_schedule_is_a_queue():
    """Steps that became ready first run first: b before c when both wait only on a."""
    schedule = function("schedule")
    assert schedule({{"a": [], "b": ["a"], "c": ["a"], "d": ["c", "b"]}}) == ["a", "b", "c", "d"]


def test_edit_distance():
    """kitten to sitting is 3, flaw to lawn is 2, and a string to itself is 0."""
    edit_distance = function("edit_distance")
    assert (edit_distance("kitten", "sitting"), edit_distance("flaw", "lawn"), edit_distance("same", "same")) == (3, 2, 0)
''',
)
write("exercises/debug-a-slow-pipeline/wrong/still-a-list.py", DEBUG_STILL_LIST)
write("exercises/debug-a-slow-pipeline/wrong/still-a-stack.py", DEBUG_STILL_LIFO)
write("exercises/debug-a-slow-pipeline/wrong/still-bottom-up.py", DEBUG_STILL_ROWS)
write(
    "exercises/debug-a-slow-pipeline/wrong/typed-in.py",
    "def dedupe(records, key):\n    return records\n\n\ndef schedule(steps):\n    return list(steps)\n\n\ndef edit_distance(a, b):\n    return 0\n\n\n"
    + "".join(f"print({line!r})\n" for line in EXPECTED["main"].splitlines()),
)

# =====================================================================================
# the way through: a solved sibling
# =====================================================================================

write(
    "exercises/example-a-pipeline-by-hand/exercise.yaml",
    f'''id: example-a-pipeline-by-hand
stage: worked_example
rev: 1
title: "A pipeline by hand"
prompt: |
  The checkpoint's five tools, run on four sensor readings. Press **Run**, then read how each part works; the checkpoint is the same tools on a bigger dataset, with the checks counting what they cost.
steps:
  - label: "Dedupe: a set beside a list"
    lines: "{ln('def dedupe')}-{ln('    return kept')}"
    note: "One pass. The set remembers the keys seen so far, so `record[key] not in seen` is a constant-time lookup; the list keeps the first record for each key in the order it came. A list for `seen` would scan, and the checkpoint's checks would count it."
  - label: "Top k: a heap of at most k"
    lines: "{ln('def top_k')}-{ln('    return [record for value, i, record in sorted')}"
    note: "Each record is pushed as `(value, -index, record)`; when the heap holds more than `k`, the smallest is popped, so the heap always holds the `k` largest seen. The `-index` breaks ties so that the earlier record wins and the records themselves are never compared. At the end the few survivors are sorted, largest first."
  - label: "Join: index one side, scan the other"
    lines: "{ln('def join')}-{ln('    return merged')}"
    note: "The right side is grouped by key in a dict of lists, one pass; then each left record looks its key up and merges with every match. Left records with no match are dropped, as are right records nothing refers to."
  - label: "Edit distance, and the closest name"
    lines: "{ln('def edit_distance')}-{ln('    return best, best_distance')}"
    note: "The dynamic-programming table from the last topic: first row and column are lengths, each cell the cheapest of delete, insert and substitute or match. `closest_name` tries every candidate and keeps the smallest distance, the first on a tie."
  - label: "Schedule: Kahn's algorithm over dependencies"
    lines: "{ln('def schedule')}-{ln('    return order')}"
    note: "Each step counts how many dependencies it still waits for; the ready queue starts with the steps that wait for none; running a step decrements its dependents and queues any that reach zero. Steps left over mean a cycle, which is an error. The queue is what makes steps run in the order they became ready."
  - label: "Four readings through the pipeline"
    lines: "{ln('readings = [')}-{ln('print(schedule(')}"
    note: "Four readings, one duplicated, from three sensors; the top two by value; the join with the rooms (s2 has no room and is dropped); kitten to sitting is 3 and `hal` is one edit from `hall`; and the schedule reads, calibrates, then stores and plots in the order they became ready."
''',
)
write("exercises/example-a-pipeline-by-hand/solution.py", EXAMPLE)
write(
    "exercises/example-a-pipeline-by-hand/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the five lines of the tiny pipeline."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

# =====================================================================================
# the way through: the build in steps
# =====================================================================================


def write_step(folder, title, prompt, hints, starter, solution, tests, wrong_name, wrong, typed_in):
    write(
        f"exercises/{folder}/exercise.yaml",
        f'''id: {folder}
stage: fill_in
rev: 1
title: "{title}"
prompt: |
{block(prompt)}hints:
{"".join("  - " + json.dumps(h) + chr(10) for h in hints)}''',
    )
    write(f"exercises/{folder}/starter.py", starter)
    write(f"exercises/{folder}/solution.py", solution)
    write(f"exercises/{folder}/test_exercise.py", tests)
    write(f"exercises/{folder}/wrong/{wrong_name}.py", wrong)
    write(f"exercises/{folder}/wrong/typed-in.py", typed_in)


write_step(
    "step-dedupe",
    "Step 1: dedupe with a set",
    f"The first piece of the checkpoint. Replace each `...` so `seen` is a set and each new key is added to it, and the program prints the distinct ids in the order they first appear:\n\n```\n{STEP1_OUT}```\n",
    ["`set()` makes an empty set; a list would make every check a scan.", "A set gains an element with `add`."],
    STEP1_STARTER,
    STEP1_SOLUTION,
    f'''from checks import function, run
{TRACKED}

def test_the_output():
    """Prints the three distinct ids."""
    printed = run()
    assert printed == {STEP1_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_scales():
    """3,000 records with 1,500 distinct keys dedupe within 30,000 comparisons."""
    dedupe = function("dedupe")
    records = [{{"key": key, "n": i}} for i, key in enumerate(tracked(i % 1500 for i in range(3000)))]
    Tracked.compared = 0
    assert len(dedupe(records, "key")) == 1500
    assert Tracked.compared < 30_000
''',
    "a-list",
    STEP1_SOLUTION.replace("seen = set()", "seen = []").replace("seen.add(", "seen.append("),
    "def dedupe(records, key):\n    return records[:3]\n\n\n" + "".join(f"print({line!r})\n" for line in STEP1_OUT.splitlines()),
)

write_step(
    "step-top-k",
    "Step 2: top k through a heap",
    f"The second piece. Replace each `...` so the heap is trimmed whenever it holds more than `k` entries, by popping its smallest, and the program prints the two largest spends' ids and then all five in order:\n\n```\n{STEP2_OUT}```\n",
    ["The heap may hold `k` entries; one more than that is one too many.", "`heapq.heappop` removes the smallest entry and keeps the heap in order; a list's `pop` would remove the wrong one."],
    STEP2_STARTER,
    STEP2_SOLUTION,
    f'''from checks import function, run


def test_the_output():
    """Prints the top two and the full order."""
    printed = run()
    assert printed == {STEP2_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_ties_keep_the_earlier():
    """Among equal values the earlier record comes first, and k above the length returns everything."""
    top_k = function("top_k")
    records = [{{"v": 5, "n": 0}}, {{"v": 9, "n": 1}}, {{"v": 5, "n": 2}}, {{"v": 9, "n": 3}}]
    assert [r["n"] for r in top_k(records, "v", 2)] == [1, 3]
    assert [r["n"] for r in top_k(records, "v", 9)] == [1, 3, 0, 2]
''',
    "pops-the-end",
    STEP2_SOLUTION.replace("heapq.heappop(heap)", "heap.pop()"),
    "import heapq\n\n\ndef top_k(records, field, k):\n    return records[:k]\n\n\n" + "".join(f"print({line!r})\n" for line in STEP2_OUT.splitlines()),
)

write_step(
    "step-join",
    "Step 3: a hash join",
    f"The third piece. Replace each `...` so the right side is indexed by the join key and a left record with no match contributes nothing, and the program prints each event's id with its user's city:\n\n```\n{STEP3_OUT}```\n",
    ["The index is keyed by the same field the left side will look up: `record[key]`.", "`by_key.get(record[key], [])` gives an empty list when the key is missing, so the inner loop simply doesn't run."],
    STEP3_STARTER,
    STEP3_SOLUTION,
    f'''from checks import function, run
{TRACKED}

def test_the_output():
    """Prints the three joined rows."""
    printed = run()
    assert printed == {STEP3_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_scales():
    """1,000 left records joined with 2,000 right records give 2,000 rows within 60,000 comparisons."""
    join = function("join")
    keys = tracked(range(1000))
    left = [{{"k": key, "left": i}} for i, key in enumerate(keys)]
    right = [{{"k": keys[i % 1000], "right": i}} for i in range(2000)]
    Tracked.compared = 0
    assert len(join(left, right, "k")) == 2000
    assert Tracked.compared < 60_000
''',
    "scans",
    STEP3_SOLUTION.replace(
        "    by_key = {}\n    for record in right:\n        by_key.setdefault(record[key], []).append(record)\n    merged = []\n    for record in left:\n        for match in by_key.get(record[key], []):\n            merged.append({**record, **match})",
        "    merged = []\n    for record in left:\n        for match in right:\n            if match[key] == record[key]:\n                merged.append({**record, **match})",
    ),
    "def join(left, right, key):\n    return []\n\n\n" + "".join(f"print({line!r})\n" for line in STEP3_OUT.splitlines()),
)

write_step(
    "step-schedule",
    "Step 4: a schedule by queue",
    f"The last piece before the full build. Replace each `...` so that running a step reduces each dependent's count of outstanding dependencies by one and queues the dependent when nothing remains, and the program prints the five-step order and the cycle's error:\n\n```\n{STEP4_OUT}```\n",
    ["Each finished dependency is one fewer to wait for.", "A step with nothing left to wait for is ready: its count is zero."],
    STEP4_STARTER,
    STEP4_SOLUTION,
    f'''from checks import function, run


def test_the_output():
    """Prints the order and the cycle's message."""
    printed = run()
    assert printed == {STEP4_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_a_diamond_and_a_chain():
    """A diamond runs its two middle steps in the order they became ready, and a chain of 50 runs in chain order."""
    schedule = function("schedule")
    assert schedule({{"d": ["c", "b"], "a": [], "b": ["a"], "c": ["a"]}}) == ["a", "b", "c", "d"]
    chain = {{"s0": []}}
    for i in range(1, 50):
        chain[f"s{{i}}"] = [f"s{{i - 1}}"]
    assert schedule(chain) == [f"s{{i}}" for i in range(50)]
''',
    "never-releases",
    STEP4_SOLUTION.replace("            remaining[dependent] -= 1\n            if remaining[dependent] == 0:", "            if remaining[dependent] == 0:"),
    "from collections import deque\n\n\ndef schedule(steps):\n    return list(steps)\n\n\n" + "".join(f"print({line!r})\n" for line in STEP4_OUT.splitlines()),
)

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.m6.checkpoint
kind: checkpoint
status: ready
title: "Checkpoint 6: the algorithms behind a pipeline"
summary: "A small data pipeline built from the module's tools: deduplicate and join records with hashing, keep the top k with a heap, match near-duplicate names by edit distance, and order the pipeline's steps by topological sort, each at the right cost."
prerequisites: [ml.dsa.arrays-and-hashing, ml.dsa.graphs, ml.dsa.dynamic-programming]
estimated_minutes: 120
rev: 1
objectives:
  - "Build the pieces of a small data pipeline (deduplicate, join, top-k, near-duplicate matching, step ordering) and show by counting steps that each scales as its order of growth says."
  - "Find and fix three bugs that each make a step quadratic or wrong: a nested-loop lookup where a set belongs, a queue popped from the wrong end, and a table filled in the wrong order."
  - "Explain why a dictionary lookup is constant time on average, and what a topological order guarantees."
prove:
  build: build-a-pipeline-toolkit
  debug: debug-a-slow-pipeline
  explain:
    prompt: |
      Your pipeline toolkit is in code review. The reviewer asks three things. First: "`record[key] not in seen` is one line either way; why is it fast when `seen` is a set and slow when it is a list, and what does 'constant time on average' actually depend on?" Second: "what does `schedule`'s order guarantee, how does it find it, and what happens if two steps depend on each other?" Third: "give me the order of growth of each of the five pieces, and tell me how you would check one of them by experiment." In your own words, answer all three.
    rubric:
      - id: hashing
        required: true
        description: "A set is a hash table: the key's hash picks a bucket and only the few keys there are compared, so a lookup costs about the same however many keys there are; a list's `in` scans from the front, so a lookup inside a loop makes the whole thing quadratic. 'On average' depends on the hash spreading keys across buckets and the table growing; a bad hash piles keys into one bucket and the lookup becomes a scan. Keys must be hashable."
      - id: topo
        required: true
        description: "A topological order lists the steps so that every step comes after everything it depends on; Kahn's algorithm counts each step's outstanding dependencies, starts with those that have none, and releases a step when its count reaches zero, taking ready steps from a queue in the order they became ready. Steps left over mean a cycle, which no order can satisfy, so it is an error."
      - id: orders
        required: true
        description: "dedupe and the hash join are linear in the records (one pass, constant-time lookups); top-k is n log k; closest_name is the number of names times the product of the two lengths (the table); schedule is steps plus dependencies. A list for seen or a nested-loop join would be quadratic."
      - id: doubling
        required: true
        description: "Double the input and measure again, counting steps or timing the best of a few runs: linear doubles, n log n a little more than doubles, quadratic quadruples; repeat the doubling to confirm."
    model_answer: |
      The line is the same but the structure underneath it isn't. A set is a hash table: it turns the key into a number, uses that number to pick a bucket, and compares the key only with the handful of keys in that bucket, so a lookup costs about the same whether the set holds ten keys or a million. A list has no such shortcut; `in` compares the key with the elements one by one from the front, so a lookup costs as many steps as there are elements, and a lookup inside a loop over the records makes the whole dedupe quadratic. The phrase "constant time on average" is honest about what it depends on: the hash function has to spread keys across the buckets, and the table has to grow as keys arrive so the buckets stay short. With a bad hash that sends every key to the same bucket, the set is a list in disguise. That is also why keys must be hashable, which in practice means unchangeable, like strings, numbers and tuples. The schedule's order guarantees that every step appears after every step it depends on, so running the steps in that order never reaches a step whose inputs don't exist yet. It finds the order by counting, for each step, how many of its dependencies are still outstanding, starting with the steps that have none, and whenever a step runs, reducing the counts of the steps that depend on it and queueing any that reach zero. Because ready steps wait in a queue, they run in the order they became ready. If two steps depend on each other, neither count ever reaches zero, so they are left over when the queue runs dry, and the function raises an error, because no order can satisfy a cycle. As for growth: dedupe is linear in the number of records, one pass with a constant-time set lookup per record; the join is linear in the two sides together, one pass to index the right side and one pass over the left with a constant-time lookup each; top-k is n log k, a push and a pop on a heap of at most k entries per record; closest name is the number of candidate names times the product of the two string lengths, because each edit-distance table has one cell per pair of prefixes; and the schedule is linear in the steps plus the dependencies, since each dependency is counted once and decremented once. To check one by experiment I would double its input and measure again, counting comparisons if I can instrument it or timing the best of a few runs if not: a linear piece should take about twice as long, top-k a little more than twice, and anything that quadruples has a scan hiding in it.
# For a learner who's stuck on the build (ADR-0012): a solved sibling, the
# build in steps with hints, then fresh versions.
unstuck:
  example: example-a-pipeline-by-hand
  steps: [step-dedupe, step-top-k, step-join, step-schedule]
  versions: [build-a-pipeline-toolkit-logs, build-a-pipeline-toolkit-catalog]
''',
)

print("ml.m6.checkpoint written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
