"""Writes the topic ml.dsa.arrays-and-hashing (Module 6's second topic). Run
from the repository root under uv (python -m uv run python <this file>), so
every program's expected output is captured from CPython rather than typed in.
The worked example's hash function is written out, so its collisions are the
same in both runtimes. Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.dsa.arrays-and-hashing")


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

EXAMPLE = '''def string_hash(key):
    """A hash function you can see: mix each character in, wrapping at 2**32."""
    h = 0
    for ch in key:
        h = (h * 31 + ord(ch)) % 2**32
    return h


class HashTable:
    """A dict built by hand: a list of buckets, each a short list of (key, value) pairs."""

    def __init__(self, hash_function=string_hash):
        self.hash_function = hash_function
        self.buckets = [[] for _ in range(4)]
        self.count = 0
        self.compared = 0

    def bucket_for(self, key):
        return self.buckets[self.hash_function(key) % len(self.buckets)]

    def get(self, key):
        for stored_key, value in self.bucket_for(key):
            self.compared += 1
            if stored_key == key:
                return value
        raise KeyError(key)

    def put(self, key, value):
        bucket = self.bucket_for(key)
        for i, (stored_key, _) in enumerate(bucket):
            self.compared += 1
            if stored_key == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self.count += 1
        if self.count > 2 * len(self.buckets) // 3:
            self.grow()

    def grow(self):
        pairs = [pair for bucket in self.buckets for pair in bucket]
        self.buckets = [[] for _ in range(2 * len(self.buckets))]
        for key, value in pairs:
            self.bucket_for(key).append((key, value))


names = [f"user{i}" for i in range(1000)]

table = HashTable()
for i, name in enumerate(names):
    table.put(name, i)
table.compared = 0
for name in names:
    table.get(name)
print("good hash:", len(table.buckets), "buckets, longest", max(len(b) for b in table.buckets), "| 1000 lookups:", table.compared, "comparisons")

bad = HashTable(hash_function=len)
for i, name in enumerate(names):
    bad.put(name, i)
bad.compared = 0
for name in names:
    bad.get(name)
print("bad hash:", len(bad.buckets), "buckets, longest", max(len(b) for b in bad.buckets), "| 1000 lookups:", bad.compared, "comparisons")

compared = 0
for name in names:
    for candidate in names:
        compared += 1
        if candidate == name:
            break
print("list scans: 1000 lookups:", compared, "comparisons")

real = {name: i for i, name in enumerate(names)}
print("Python's dict agrees:", all(real[name] == table.get(name) for name in names))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
GOOD = EX[0].split()
BAD = EX[1].split()
GOOD_BUCKETS, GOOD_LONGEST, GOOD_COMPARED = int(GOOD[2]), int(GOOD[5]), int(GOOD[9])
BAD_BUCKETS, BAD_LONGEST, BAD_COMPARED = int(BAD[2]), int(BAD[5]), int(BAD[9])
assert GOOD_BUCKETS == 2048 and GOOD_LONGEST <= 8 and 1000 <= GOOD_COMPARED <= 1600, EX[0]
assert BAD_BUCKETS == 2048 and BAD_LONGEST >= 300 and BAD_COMPARED >= 100000, EX[1]
assert EX[2] == "list scans: 1000 lookups: 500500 comparisons" and EX[3] == "Python's dict agrees: True", EX[2:]
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


def thousands(n: int) -> str:
    return f"{n:,}"


# --- recall programs ----------------------------------------------------------------------------

PREDICT_SHIFT = '''def insert_at_front(items, value):
    """What list.insert(0, value) has to do: make room, then shift everything along."""
    items.append(None)
    moves = 0
    for i in range(len(items) - 1, 0, -1):
        items[i] = items[i - 1]
        moves += 1
    items[0] = value
    return moves


items = [10, 20, 30]
print(insert_at_front(items, 5), items)
print(insert_at_front(items, 1), items)
'''
PREDICT_SHIFT_OUT = out(PREDICT_SHIFT)
assert PREDICT_SHIFT_OUT == "3 [5, 10, 20, 30]\n4 [1, 5, 10, 20, 30]\n", PREDICT_SHIFT_OUT

REVIEW_BUCKET = '''def tiny_hash(key):
    return sum(ord(ch) for ch in key)


for key in ("cat", "act", "dog"):
    print(key, tiny_hash(key), tiny_hash(key) % 8)
'''
REVIEW_BUCKET_OUT = out(REVIEW_BUCKET)
assert REVIEW_BUCKET_OUT == "cat 312 0\nact 312 0\ndog 314 2\n", REVIEW_BUCKET_OUT

PARSONS_LINES = [
    'words = ["a", "b", "a", "c", "a"]',
    "counts = {}",
    "for word in words:",
    "    counts[word] = counts.get(word, 0) + 1",
    'print(counts["a"], len(counts))',
]
assert out("\n".join(PARSONS_LINES) + "\n") == "3 3\n"

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''def group_by(records, field):
    """{value of the field: [the records with that value]}, first appearance first."""
    groups = {}
    for record in records:
        groups.setdefault(record[field], []).append(record)
    return groups


orders = [
    {"id": 1, "city": "Oslo", "total": 30},
    {"id": 2, "city": "Lima", "total": 12},
    {"id": 3, "city": "Oslo", "total": 8},
    {"id": 4, "city": "Pune", "total": 19},
    {"id": 5, "city": "Lima", "total": 41},
]
for city, group in group_by(orders, "city").items():
    print(city, len(group), sum(order["total"] for order in group))
'''
FILL_STARTER = FILL_SOLUTION.replace("groups.setdefault(record[field], [])", "groups.setdefault(record[...], ...)")
FILL_WRONG = FILL_SOLUTION.replace("        groups.setdefault(record[field], []).append(record)", "        groups[record[field]] = [record]")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "Oslo 2 38\nLima 2 53\nPune 1 19\n", FILL_OUT
assert out(FILL_WRONG) != FILL_OUT

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''def two_sum(numbers, target):
    """A pair of values from the list adding to target, as (earlier, later), or None; one pass."""
    seen = set()
    for number in numbers:
        if target - number in seen:
            return (target - number, number)
        seen.add(number)
    return None


print(two_sum([3, 9, 14, 5, 11], 20))
print(two_sum([3, 9, 14, 5, 11], 100))
print(two_sum([8, 8], 16))
'''
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "(9, 11)\nNone\n(8, 8)\n", WRITE_OUT
WRITE_WRONG = WRITE_SOLUTION.replace("return (target - number, number)", "return (number, target - number)")
assert out(WRITE_WRONG) != WRITE_OUT

# --- the build ----------------------------------------------------------------------------------

BUILD_SOLUTION = '''def count_frequencies(items):
    """{value: how many times it appears}, in one pass."""
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts


def dedupe(items):
    """The distinct values, first appearance first."""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def group_by(records, field):
    """{value of the field: [the records with that value]}."""
    groups = {}
    for record in records:
        groups.setdefault(record[field], []).append(record)
    return groups


def join(left, right, field):
    """Every left record merged with every right record sharing its field value (right's fields win), in left order."""
    by_key = group_by(right, field)
    merged = []
    for record in left:
        for match in by_key.get(record[field], []):
            merged.append({**record, **match})
    return merged


words = "the cat sat on the mat the end".split()
print(count_frequencies(words))
print(dedupe(words))
people = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Grace"}, {"id": 3, "name": "Linus"}]
orders = [{"id": 2, "item": "lamp"}, {"id": 1, "item": "book"}, {"id": 2, "item": "pen"}, {"id": 9, "item": "cup"}]
print(sorted(group_by(orders, "id")))
print(join(people, orders, "id"))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == (
    "{'the': 3, 'cat': 1, 'sat': 1, 'on': 1, 'mat': 1, 'end': 1}\n"
    "['the', 'cat', 'sat', 'on', 'mat', 'end']\n"
    "[1, 2, 9]\n"
    "[{'id': 1, 'name': 'Ada', 'item': 'book'}, {'id': 2, 'name': 'Grace', 'item': 'lamp'}, {'id': 2, 'name': 'Grace', 'item': 'pen'}]\n"
), BUILD_OUT
BUILD_NESTED_JOIN = BUILD_SOLUTION.replace(
    '''    by_key = group_by(right, field)
    merged = []
    for record in left:
        for match in by_key.get(record[field], []):
            merged.append({**record, **match})
    return merged''',
    '''    merged = []
    for record in left:
        for match in right:
            if match[field] == record[field]:
                merged.append({**record, **match})
    return merged''',
)
BUILD_COUNT_SCANS = BUILD_SOLUTION.replace(
    "    counts = {}\n    for item in items:\n        counts[item] = counts.get(item, 0) + 1\n    return counts",
    "    counts = {}\n    for item in items:\n        counts[item] = items.count(item)\n    return counts",
)
BUILD_GROUP_OVERWRITES = BUILD_SOLUTION.replace("        groups.setdefault(record[field], []).append(record)", "        groups[record[field]] = [record]")
assert out(BUILD_NESTED_JOIN) == BUILD_OUT and out(BUILD_COUNT_SCANS) == BUILD_OUT and out(BUILD_GROUP_OVERWRITES) != BUILD_OUT

TRACKED = '''

class Tracked:
    """A value that counts how often it is compared. Hashing is free; == is counted."""

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

DEBUG_SOLUTION = '''def group_by(records, field):
    groups = {}
    for record in records:
        groups.setdefault(record[field], []).append(record)
    return groups


def join(left, right, field):
    """Every left record merged with every right record sharing its field value, in left order."""
    by_key = group_by(right, field)
    merged = []
    for record in left:
        for match in by_key.get(record[field], []):
            merged.append({**record, **match})
    return merged


people = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Grace"}]
orders = [{"id": 2, "item": "lamp"}, {"id": 1, "item": "book"}, {"id": 2, "item": "pen"}]
print(join(people, orders, "id"))

left = [{"id": i} for i in range(2000)]
right = [{"id": i % 1000, "n": i} for i in range(2000)]
print(len(join(left, right, "id")))
'''
BUG_OVERWRITE = ("        groups.setdefault(record[field], []).append(record)", "        groups[record[field]] = [record]")
BUG_NESTED = (
    '''    by_key = group_by(right, field)
    merged = []
    for record in left:
        for match in by_key.get(record[field], []):
            merged.append({**record, **match})
    return merged''',
    '''    merged = []
    for record in left:
        for match in right:
            if match[field] == record[field]:
                merged.append({**record, **match})
    return merged''',
)
DEBUG_OVERWRITE_ONLY = DEBUG_SOLUTION.replace(*BUG_OVERWRITE)
DEBUG_NESTED_ONLY = DEBUG_SOLUTION.replace(*BUG_NESTED)
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_OVERWRITE).replace(*BUG_NESTED)
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT + "overwrite only:\n" + out(DEBUG_OVERWRITE_ONLY) + "starter:\n" + out(DEBUG_STARTER))
assert DEBUG_OUT == "[{'id': 1, 'name': 'Ada', 'item': 'book'}, {'id': 2, 'name': 'Grace', 'item': 'lamp'}, {'id': 2, 'name': 'Grace', 'item': 'pen'}]\n2000\n", DEBUG_OUT
assert out(DEBUG_OVERWRITE_ONLY).splitlines()[1] == "1000"
assert out(DEBUG_NESTED_ONLY) == DEBUG_OUT
# With both bugs, the index is never consulted, so the starter prints the right answer and is only slow.
assert out(DEBUG_STARTER) == DEBUG_OUT

REVIEW_CODE_SOLUTION = '''def count_words(text):
    """{word: how many times it appears in the text}."""
    counts = {}
    for word in text.split():
        counts[word] = counts.get(word, 0) + 1
    return counts


counts = count_words("to be or not to be")
print(counts["to"], counts["be"], counts["or"], len(counts))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "2 2 1 4\n", REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.dsa.arrays-and-hashing
kind: topic
status: ready
title: "Arrays, hash tables and sets"
summary: "What a list, a dict and a set cost per operation and why: contiguous arrays, amortized appends, hash functions and buckets; and the patterns they make fast: counting, deduplicating, grouping and joining."
prerequisites: [ml.dsa.complexity]
estimated_minutes: 55
rev: 1
objectives:
  - "Say what indexing, appending, inserting at the front and searching a list cost, and why an array makes them so."
  - "Explain how a hash table turns a key into a bucket, what a collision is, and why dict and set lookups are constant time on average."
  - "Replace a nested-loop search with a dict or a set, and measure the difference."
  - "Count frequencies, deduplicate, group by key and join two tables with dictionaries."
# Linked, never copied or embedded: the Runestone book is CC BY-NC-SA 4.0;
# Open Data Structures is CC BY 2.5; the Python documentation is under the
# PSF licence.
resources:
  - title: "Problem Solving with Algorithms and Data Structures using Python (Brad Miller and David Ranum), section 6.5: Hashing (hash functions, collisions, load factor), and sections 3.6 and 3.7 on the performance of lists and dictionaries"
    url: https://runestone.academy/ns/books/published/pythonds3/SortSearch/Hashing.html
    type: reading
    use: link
    license: CC BY-NC-SA 4.0
  - title: "Open Data Structures in Python (Pat Morin), chapter 5: Hash Tables, the introduction and section 5.1"
    url: https://opendatastructures.org/ods-python/5_Hash_Tables.html
    type: reading
    use: link
    license: CC BY 2.5
  - title: "The Python tutorial, chapter 5: Data Structures (lists as stacks and queues, sets, dictionaries)"
    url: https://docs.python.org/3/tutorial/datastructures.html
    type: reading
    use: link
    license: "PSF licence (linked, not copied)"
practice:
  - example-a-hash-table-by-hand
  - parsons-count-words
  - predict-a-list-shift
  - mcq-why-pop-zero-is-slow
  - mcq-what-a-collision-is
  - mcq-a-bad-hash
  - mcq-set-or-list
  - fill-group-by-key
  - write-two-sum
prove:
  build: build-a-tiny-data-toolkit
  debug: debug-a-slow-join
  explain:
    prompt: |
      A teammate's pipeline builds its vocabulary with `if word not in vocab: vocab.append(word)` where `vocab` is a list, and joins two tables with a loop inside a loop. It is fine on 10,000 rows and hopeless on a million. In your own words: what is a hash table, and how does a dict find a key without scanning? What does "constant time on average" depend on, and what is a collision? Why are a list's `in` and `insert(0, ...)` linear while `append` isn't? And how would you rewrite both pieces, and check the rewrite with the doubling test?
    rubric:
      - id: hashing
        required: true
        description: "A hash function turns the key into a number; that number modulo the bucket count picks a bucket; the lookup compares only the few keys in that bucket. Two keys in one bucket is a collision; the table grows (and re-places every key) to keep buckets short."
      - id: average
        required: true
        description: "Constant time on average depends on the hash spreading keys across buckets; a bad hash (or an adversary) puts everything in one bucket and the lookup becomes a list scan. Keys must be hashable, so unchangeable: strings, numbers, tuples."
      - id: list-costs
        required: true
        description: "A list is a contiguous array: an index is one step; `in` scans from the front; `insert(0, ...)` and `pop(0)` shift every element; `append` is constant on average because the list keeps spare room and grows in jumps (amortized)."
      - id: rewrite
        required: true
        description: "Keep a set beside the vocabulary list (or build the vocabulary as a dict word to index); index one table by key in a dict of lists and scan the other once (a hash join). Check by doubling the rows: the rewrite's time doubles, the old version's quadruples."
    model_answer: |
      A hash table is the structure behind Python's dict and set. It keeps a list of buckets, and a hash function turns each key into a number; that number taken modulo the number of buckets says which bucket the key lives in. To find a key, the table computes its bucket and compares the key only with the few keys stored there, instead of scanning everything. Two keys that land in the same bucket are a collision, which is normal and harmless as long as it stays rare: when the table gets about two-thirds full it doubles its buckets and re-places every key, so the buckets stay short. That is what "constant time on average" depends on: a hash function that spreads keys evenly and a table that grows. With a bad hash that sends every key to the same bucket, the lookup degenerates into a scan of a list, which is why the honest claim is "on average". Keys must also be hashable, which in practice means unchangeable, like strings, numbers and tuples; a list can't be a key because its contents, and so its hash, could change after it was filed. A list is different: it is one contiguous block of references, so reading item i is a single step, but `in` has to look at the items one by one from the front, and inserting or popping at index 0 has to shift every other element along by one. `append` is cheap because the list keeps spare room at the end and, when it runs out, grows in a jump, so most appends are instant and the occasional copy is paid for by the many; that is what amortized constant time means. For the vocabulary I would keep a set of the words seen beside the list, or build the vocabulary directly as a dict from word to index, so the membership test is a hash lookup instead of a scan. For the join I would index one table by the join key in a dict of lists, then make one pass over the other table looking each key up, a hash join. To check, I would double the number of rows and time both versions: the rewrite should take about twice as long, the old versions about four times.
review_pool:
  - review-predict-bucket-index
  - review-mcq-why-on-average
  - review-mcq-which-structure
  - review-count-words
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: list-costs
    description: "Say what each list operation costs and why a contiguous array makes it so"
  - id: hashing
    description: "Explain how a hash table finds a key, what a collision is, and why lookups are constant time on average"
  - id: replace
    description: "Replace a nested-loop search with a dict or a set, and measure the difference"
  - id: patterns
    description: "Count, deduplicate, group and join with dictionaries"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

The last topic found that a set turns a quadratic search into a linear one. This topic is why. A **list** is an **array**, one block of memory with its items in order, which makes some operations one step and others a shift of everything. A **dict** or **set** is a **hash table**, which turns a key into a bucket number and looks only there. The worked example builds a hash table by hand, with a hash function you can read, and counts the comparisons it makes against a list scan; then a bad hash function shows what "constant time on average" depends on.

The main resource is **_Problem Solving with Algorithms and Data Structures using Python_, section 6.5, Hashing**, with the book's sections 3.6 and 3.7 on what list and dict operations cost; about 30 minutes. The Python tutorial's chapter 5 is the reference for the operations themselves. Watch for:

- **The hash function** picks the bucket; nothing is searched.
- **Collisions** are normal; a table grows to keep them rare.
- **The table of costs** for lists and dicts, operation by operation.

</Intro>

<Resource index={{0}} />

<Recap>

- **A list is an array:** one block of memory holding references in order. So `items[i]` is one step (`O(1)`); `append` is `O(1)` on average (**amortized**: the list keeps spare room at the end and grows in jumps, so most appends are instant and the occasional copy is paid for by the many); `pop()` from the end is `O(1)`. But `insert(0, x)` and `pop(0)` shift every element along (`O(n)`), and `x in items`, `items.index(x)` and `items.count(x)` scan from the front (`O(n)`). The worked example's list scan makes 500,500 comparisons for 1,000 lookups.
- **A hash table** is what `dict` and `set` are. A **hash function** turns a key into a number (the example's multiplies by 31 and adds each character's code); that number modulo the number of **buckets** picks the bucket; a lookup goes straight to the bucket and compares only the few keys there. Two keys in one bucket are a **collision**. When the table is about two-thirds full it **grows**: doubles its buckets and re-places every key, so buckets stay short. Keys must be **hashable**, which means unchangeable: strings, numbers, tuples. A list can't be a key, because its hash would change when it did.
- **`O(1)` on average, and what that depends on.** With the readable hash, 1,000 lookups among 1,000 names cost {thousands(GOOD_COMPARED)} comparisons, about {GOOD_COMPARED / 1000:.1f} each, with {GOOD_BUCKETS:,} buckets and a longest bucket of {GOOD_LONGEST}. With `len` as the hash function, every name lands in one of three buckets (the longest holds {BAD_LONGEST}) and the same lookups cost {thousands(BAD_COMPARED)} comparisons, {BAD_COMPARED // GOOD_COMPARED} times as many: a list in disguise. Python's own hash functions are good, and "on average" is the honest word for what they give you.
- **Replace the scan.** `x in a_list` inside a loop is the commonest quadratic in data code; a set or dict built once turns it into one pass. The doubling test from the last topic tells you which you have: time doubles, or quadruples.
- **The patterns:** count with `counts[key] = counts.get(key, 0) + 1` (or `collections.Counter`); deduplicate keeping order with a set beside a list; group with `groups.setdefault(key, []).append(record)` (or `collections.defaultdict(list)`); **join** two tables by indexing one side by its key in a dict of lists and scanning the other side once (a **hash join**); find two numbers that add to a target by remembering what you've seen.
- **In machine learning:** a vocabulary (word to index), a label encoder and a feature lookup are hash tables; the join that builds a training table from several sources is a hash join (that is what `pandas.merge` does); and the quadratic that eats a pipeline is almost always a list where a set belonged.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-count-words.yaml",
    "id: parsons-count-words\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to count how often each word appears, and print `3 3` (three `\"a\"`s, three distinct words). One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("    counts[word] = counts[word] + 1")
    + "\nexplanation: |\n"
    + block("`counts.get(word, 0)` returns the count so far, or 0 for a word not yet seen, so the first time a word appears it becomes 1. The decoy indexes `counts[word]` directly, which raises `KeyError` on the first word. Three `\"a\"`s, and three distinct keys.")
    + "skills: [patterns]\n",
)

write(
    "recall/predict-a-list-shift.yaml",
    f'''id: predict-a-list-shift
type: predict_output
rev: 1
prompt: |
  What `list.insert(0, value)` has to do, written out: make room at the end, then move every element along by one. What does the program print?
code: |
{block(PREDICT_SHIFT)}expected_output: |
{block(PREDICT_SHIFT_OUT)}explanation: |
  Three items have to move for the first insert and four for the second: inserting at the front costs one move per existing element, which is why `insert(0, ...)` and `pop(0)` are linear and `append` and `pop()` are not. The list is an array; there is no free slot at the front.
skills: [list-costs]
''',
)

mcq(
    "mcq-why-pop-zero-is-slow",
    "A queue is kept as a list of a million tasks, and each task is taken with `tasks.pop(0)`. Why is each `pop(0)` slow?",
    [
        "Because the list has to be searched for the smallest element first",
        "Because every one of the remaining elements shifts down one place",
        "Because Python copies the whole list before removing anything, to keep it safe",
        "It isn't slow; `pop(0)` and `pop()` cost the same, one step each",
    ],
    1,
    "A list is an array with its items in order, so removing the first one leaves a gap that every other element shifts along to fill: a million moves per pop. `pop()` from the end leaves no gap and is one step. A queue wants `collections.deque`, which the next topic uses.",
    ["list-costs"],
)

mcq(
    "mcq-what-a-collision-is",
    "In a hash table, what is a collision, and what does the table do about it?",
    [
        "Two keys with the same hash value; the second one replaces the first, which is why keys must be unique",
        "Two keys that land in the same bucket; both are kept there, and growth keeps buckets short",
        "A lookup for a key that isn't there; the table raises `KeyError` instead of returning a default",
        "Two values that happen to be equal; the table stores only one of them to save space",
    ],
    1,
    "The hash function plus the modulo send two different keys to one bucket now and then; the bucket holds both and a lookup compares the few keys in it. Nothing is lost. What keeps the buckets short is growth: at about two-thirds full the table doubles its buckets and re-places every key. A missing key is not a collision, and equal values are irrelevant; keys are what is hashed.",
    ["hashing"],
)

mcq(
    "mcq-a-bad-hash",
    "The worked example's table is given `len` as its hash function, so every key goes to the bucket for its length. What happens to lookups?",
    [
        "They fail, because different keys can't share a bucket and the second one is rejected",
        "Nothing changes, because the table grows until every key has its own bucket anyway",
        "They become a scan of a long list: nearly every key is in one of a few buckets",
        "They get faster, because `len` is far cheaper to compute than a real hash function",
    ],
    2,
    "Growth adds buckets, but `len` keeps sending every name to the same three of them, so each lookup compares against a third of all the keys. Constant time on average depends on the hash spreading keys; with a bad hash the table is a list in disguise, which the example shows at hundreds of times the comparisons.",
    ["hashing"],
)

mcq(
    "mcq-set-or-list",
    "You have 10,000 customer ids and must check each against a list of a million blocked ids. Which plan is right, and why?",
    [
        "Loop over the blocked list for each id; a million steps is nothing for a computer, and it only runs once",
        "Sort both lists first, then compare them from the front; sorting makes everything after it fast",
        "Put the blocked ids in a set once, then test each id with `in`: one step per test",
        "Convert both to NumPy arrays and compare them with `==`, which vectorizes the whole comparison",
    ],
    2,
    "Ten thousand scans of a million is ten billion comparisons; a set makes the million-element build once and then each test is a constant-time lookup, about a million steps in all. Sorting would work too but costs `n log n` for no gain here, and NumPy's `==` compares positions, not membership.",
    ["replace"],
)

write(
    "recall/review-predict-bucket-index.yaml",
    f'''id: review-predict-bucket-index
type: predict_output
rev: 1
prompt: |
  A tiny hash function adds up the character codes (`c` is 99, `a` is 97, `t` is 116, `d` is 100, `o` is 111, `g` is 103), and the table has 8 buckets. What does the program print?
code: |
{block(REVIEW_BUCKET)}expected_output: |
{block(REVIEW_BUCKET_OUT)}explanation: |
  Adding codes ignores their order, so `cat` and `act` hash to the same 312 and collide in bucket 0; `dog` is 314, bucket 2. A real hash function mixes in the position of each character (the worked example multiplies by 31 before adding each one) so that anagrams usually land apart. The modulo turns any hash into a bucket index.
skills: [hashing]
''',
)

mcq(
    "review-mcq-why-on-average",
    "Why do people say a dict lookup is constant time \"on average\" rather than always?",
    [
        "Because Python sometimes stores dicts as lists when they are small, and only switches to hashing later",
        "Because collisions can pile keys into one bucket, where a lookup becomes a scan",
        "Because the first lookup of each key is slow and later ones are cached, so the average comes out constant",
        "Because the time depends on the size of the value stored under the key, which varies",
    ],
    1,
    "A lookup costs as many comparisons as there are keys in its bucket. A good hash and a table that grows keep that near one on average, but nothing forbids a bucket from filling up, and a deliberately bad hash (the worked example's `len`) turns every lookup into a scan. The size of the value never matters; the key is what is hashed.",
    ["hashing"],
)

mcq(
    "review-mcq-which-structure",
    "A pipeline step keeps the ids it has already processed in a list and checks `if id in done` before each record. It is quadratic. What is the smallest fix?",
    [
        "Make `done` a set; the check becomes a constant-time lookup and the loop one pass",
        "Sort `done` after every append so the check can use binary search",
        "Keep the list but check `done[-1000:]`, since recent ids are the likely repeats",
        "Replace the check with `done.count(id) == 0`, which is a built-in and therefore fast",
    ],
    0,
    "The scan is the problem, so replace the structure that scans. A set keeps the same `in` syntax and makes the test constant time on average. Sorting after every append costs `n log n` per record; checking only the recent ids changes the answer; and `count` is the same scan written differently.",
    ["replace"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-a-hash-table-by-hand/exercise.yaml",
    f'''id: example-a-hash-table-by-hand
stage: worked_example
rev: 1
title: "A hash table by hand"
prompt: |
  A dict built from a list of buckets and a hash function you can read, counted against a list scan, and then given a bad hash function. Press **Run**, then read how each part works.
steps:
  - label: "A hash function you can read"
    lines: "{ln('def string_hash')}-{ln('    return h')}"
    note: "A hash function turns a key into a number. This one walks the characters, multiplying the running value by 31 and adding each character's code, wrapping at `2**32` so the number stays bounded. Same key, same number, every time; different keys, usually different numbers. Python's built-in `hash` does the same job faster."
  - label: "Buckets, and which one a key goes to"
    lines: "{ln('class HashTable')}-{ln('        return self.buckets[')}"
    note: "The table starts with four empty buckets, each a list of `(key, value)` pairs. `bucket_for` takes the hash modulo the number of buckets: that is the whole trick. Nothing is searched; the key's own number says where it lives."
  - label: "Looking a key up"
    lines: "{ln('    def get')}-{ln('        raise KeyError')}"
    note: "Go to the key's bucket and compare it with the few keys there, counting each comparison. If the buckets are short, that is a handful of steps however many keys the table holds."
  - label: "Storing a key, and growing"
    lines: "{ln('    def put')}-{ln('            self.bucket_for(key).append')}"
    note: "`put` replaces the value if the key is already in its bucket, else appends the pair. When the table passes two-thirds full it doubles its buckets and re-places every key, because the modulo changes: that is what keeps buckets short as the table grows. Python's dict does the same."
  - label: "A good hash: about one comparison per lookup"
    lines: "{ln('names = [')}-{ln('good hash:')}"
    note: "A thousand names stored, then looked up: {GOOD_BUCKETS:,} buckets after growing, the longest holding {GOOD_LONGEST}, and {thousands(GOOD_COMPARED)} comparisons for 1,000 lookups, about {GOOD_COMPARED / 1000:.1f} each. That is constant time on average: the count doesn't depend on how many keys the table holds."
  - label: "A bad hash: a list in disguise"
    lines: "{ln('bad = HashTable')}-{ln('bad hash:')}"
    note: "The same table with `len` as its hash function: every name is five to seven characters long, so all thousand land in three buckets, the longest holding {BAD_LONGEST}. The same 1,000 lookups cost {thousands(BAD_COMPARED)} comparisons, {BAD_COMPARED // GOOD_COMPARED} times as many. The structure is identical; only the spread of the keys changed, and that is what \\"on average\\" depends on."
  - label: "The list scan, for comparison"
    lines: "{ln('compared = 0', ln('bad hash:'))}-{ln('list scans:')}"
    note: "Finding each name in a plain list by scanning from the front: 500,500 comparisons, about `n² / 2`, the last topic's quadratic. The good hash table did the same work in {thousands(GOOD_COMPARED)}."
  - label: "Python's dict agrees"
    lines: "{ln('real = ')}-{ln('dict agrees:')}"
    note: "A real dict built from the same names returns the same values as the hand-made table for every key. The built-in one is the same idea with a faster hash and open addressing instead of bucket lists, which the resource describes."
''',
)
write("exercises/example-a-hash-table-by-hand/solution.py", EXAMPLE)
write(
    "exercises/example-a-hash-table-by-hand/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the good hash's counts, the bad hash's, the list scan's and the agreement with dict."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-group-by-key/exercise.yaml",
    f'''id: fill-group-by-key
stage: fill_in
rev: 1
title: "Group by a key"
prompt: |
  `group_by(records, field)` should return a dict from each value of the field to the list of records that have it, in one pass. `dict.setdefault(key, default)` returns the value stored under `key`, storing and returning `default` first if the key is new. Replace each `...` so the program groups five orders by city and prints each city's order count and total:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "The key to group by is the record's value for `field`: `record[field]`."
  - "A new key should start with an empty list, so that `.append(record)` has something to append to."
skills: [patterns]
''',
)
write("exercises/fill-group-by-key/starter.py", FILL_STARTER)
write("exercises/fill-group-by-key/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-group-by-key/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the three cities with their counts and totals."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_every_record_is_kept():
    """Grouping 6 records by a field with 2 values keeps all 6, 3 in each group, in order."""
    group_by = function("group_by")
    records = [{{"k": i % 2, "n": i}} for i in range(6)]
    groups = group_by(records, "k")
    assert sorted(groups) == [0, 1]
    assert [r["n"] for r in groups[0]] == [0, 2, 4] and [r["n"] for r in groups[1]] == [1, 3, 5]
''',
)
write("exercises/fill-group-by-key/wrong/overwrites.py", FILL_WRONG)
write(
    "exercises/fill-group-by-key/wrong/typed-in.py",
    "def group_by(records, field):\n    return {}\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-two-sum/exercise.yaml",
    f'''id: write-two-sum
stage: write
rev: 1
title: "Two numbers that add up"
prompt: |
  Write `two_sum(numbers, target)`, which returns a pair of values from the list that add up to `target`, as `(earlier, later)` in the order they appear, or `None` if there is none, in **one pass**: for each number, check whether `target - number` has been seen, then remember the number. Then print it for these calls:

  ```python
  print(two_sum([3, 9, 14, 5, 11], 20))
  print(two_sum([3, 9, 14, 5, 11], 100))
  print(two_sum([8, 8], 16))
  ```

  ```
{block(WRITE_OUT)}  ```
hints:
  - "A set of the numbers seen so far makes the check a constant-time lookup."
  - "Check before you add, so a number isn't paired with itself; the two 8s are different elements."
skills: [replace]
''',
)
write("exercises/write-two-sum/starter.py", "")
write("exercises/write-two-sum/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-two-sum/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the three results."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_more_cases():
    """A number is not paired with itself; the first pair found wins; an empty list gives None."""
    two_sum = function("two_sum")
    assert two_sum([5, 1], 10) is None
    assert two_sum([1, 4, 2, 3, 6], 5) == (1, 4)
    assert two_sum([], 0) is None
''',
)
write("exercises/write-two-sum/wrong/pair-backwards.py", WRITE_WRONG)
write(
    "exercises/write-two-sum/wrong/typed-in.py",
    "def two_sum(numbers, target):\n    return (9, 11)\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-a-tiny-data-toolkit/exercise.yaml",
    f'''id: build-a-tiny-data-toolkit
stage: build
rev: 1
title: "A tiny data toolkit"
prompt: |
  Starting from a blank editor, write four functions, each in one pass with a dict or a set, never a loop inside a loop over the data:

  - `count_frequencies(items)`: a dict from each value to how many times it appears.
  - `dedupe(items)`: the distinct values as a list, first appearance first.
  - `group_by(records, field)`: a dict from each value of `field` to the list of records (dicts) that have it.
  - `join(left, right, field)`: every left record merged with every right record that has the same value of `field` (`{{**left_record, **right_record}}`, so the right record's fields win), in the order of the left records: index the right side with `group_by`, then scan the left side once.

  Then print:

  ```python
  words = "the cat sat on the mat the end".split()
  print(count_frequencies(words))
  print(dedupe(words))
  people = [{{"id": 1, "name": "Ada"}}, {{"id": 2, "name": "Grace"}}, {{"id": 3, "name": "Linus"}}]
  orders = [{{"id": 2, "item": "lamp"}}, {{"id": 1, "item": "book"}}, {{"id": 2, "item": "pen"}}, {{"id": 9, "item": "cup"}}]
  print(sorted(group_by(orders, "id")))
  print(join(people, orders, "id"))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks count how many times your code compares two keys. On 3,000 items, a one-pass count or dedupe compares a few thousand times; `items.count(x)` for each item, or a list for `seen`, compares millions of times and fails. The same for a join that scans the right side for every left record.
skills: [patterns, replace]
''',
)
write("exercises/build-a-tiny-data-toolkit/starter.py", "")
write("exercises/build-a-tiny-data-toolkit/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-a-tiny-data-toolkit/test_exercise.py",
    f'''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).
{TRACKED}

def test_the_output():
    """Prints the counts, the distinct words, the group keys and the join."""
    assert run() == {BUILD_OUT!r}


def test_count_frequencies_scales():
    """On 3,000 values with 100 distinct, the counts add up to 3,000 after fewer than 30,000 comparisons."""
    count_frequencies = function("count_frequencies")
    Tracked.compared = 0
    counts = count_frequencies(tracked([i % 100 for i in range(3000)]))
    assert len(counts) == 100 and sum(counts.values()) == 3000
    assert Tracked.compared < 30_000


def test_dedupe_scales():
    """On 3,000 values with 1,500 distinct, dedupe keeps the first-seen order after fewer than 30,000 comparisons."""
    dedupe = function("dedupe")
    Tracked.compared = 0
    result = dedupe(tracked([i % 1500 for i in range(3000)]))
    assert [item.value for item in result] == list(range(1500))
    assert Tracked.compared < 30_000


def test_join_scales():
    """Joining 2,000 left records with 2,000 right records on a key, each key matching twice, gives 2,000 rows after fewer than 60,000 comparisons."""
    join = function("join")
    left = [{{"id": key}} for key in tracked(range(1000))]
    right = [{{"id": key, "n": i}} for i, key in enumerate(tracked([i % 1000 for i in range(2000)]))]
    Tracked.compared = 0
    rows = join(left, right, "id")
    assert len(rows) == 2000 and rows[0]["id"].value == 0 and rows[0]["n"] == 0 and rows[1]["n"] == 1000
    assert Tracked.compared < 60_000


def test_group_by_keeps_every_record():
    """Grouping 6 records by a field with 2 values keeps all 6, 3 in each group."""
    group_by = function("group_by")
    groups = group_by([{{"k": i % 2, "n": i}} for i in range(6)], "k")
    assert sorted(groups) == [0, 1] and [r["n"] for r in groups[1]] == [1, 3, 5]
''',
)
write("exercises/build-a-tiny-data-toolkit/wrong/nested-join.py", BUILD_NESTED_JOIN)
write("exercises/build-a-tiny-data-toolkit/wrong/count-scans.py", BUILD_COUNT_SCANS)
write("exercises/build-a-tiny-data-toolkit/wrong/group-overwrites.py", BUILD_GROUP_OVERWRITES)
write(
    "exercises/build-a-tiny-data-toolkit/wrong/typed-in.py",
    "def count_frequencies(items):\n    return {}\n\n\ndef dedupe(items):\n    return []\n\n\ndef group_by(records, field):\n    return {}\n\n\ndef join(left, right, field):\n    return []\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-slow-join/exercise.yaml",
    f'''id: debug-a-slow-join
stage: debug
rev: 1
title: "A slow join"
prompt: |
  `join` should merge every left record with every right record that shares its `id`, and the program should print the small join and the size of a bigger one:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs, and the program prints the right answer anyway. The first makes `group_by` wrong: a new record **replaces** the group for its key instead of being appended, so an index built with it would lose `lamp` and half the bigger join. The second hides the first: `join` never uses the index, and scans every right record for every left record, a loop inside a loop. Fix both: append in `group_by`, then index the right side with it and look each left key up. The checks count the comparisons, and fail the scan.
skills: [patterns, replace]
''',
)
write("exercises/debug-a-slow-join/starter.py", DEBUG_STARTER)
write("exercises/debug-a-slow-join/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-slow-join/test_exercise.py",
    f'''from checks import function, run

EXPECTED = {DEBUG_OUT!r}
{TRACKED}

def test_the_output():
    """Prints the small join and 2000."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_group_by_keeps_every_record():
    """Grouping 6 records by a field with 2 values keeps all 6."""
    group_by = function("group_by")
    groups = group_by([{{"k": i % 2, "n": i}} for i in range(6)], "k")
    assert [r["n"] for r in groups[0]] == [0, 2, 4] and [r["n"] for r in groups[1]] == [1, 3, 5]


def test_join_scales():
    """Joining 1,000 left records with 2,000 right records gives 2,000 rows after fewer than 60,000 comparisons (the scan makes 2 million)."""
    join = function("join")
    left = [{{"id": key}} for key in tracked(range(1000))]
    right = [{{"id": key, "n": i}} for i, key in enumerate(tracked([i % 1000 for i in range(2000)]))]
    Tracked.compared = 0
    rows = join(left, right, "id")
    assert len(rows) == 2000
    assert Tracked.compared < 60_000, f"{{Tracked.compared}} comparisons: index the right side first"
''',
)
write("exercises/debug-a-slow-join/wrong/still-overwrites.py", DEBUG_OVERWRITE_ONLY)
write("exercises/debug-a-slow-join/wrong/still-scans.py", DEBUG_NESTED_ONLY)
write(
    "exercises/debug-a-slow-join/wrong/typed-in.py",
    "def group_by(records, field):\n    return {}\n\n\ndef join(left, right, field):\n    return []\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-count-words/exercise.yaml",
    f'''id: review-count-words
stage: review_code
rev: 1
title: "Count words, from memory"
prompt: |
  Write `count_words(text)`, which returns a dict from each word in the text (split on whitespace) to how many times it appears, in one pass, and print the counts of `to`, `be` and `or` and the number of distinct words in `"to be or not to be"`:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [patterns]
''',
)
write("exercises/review-count-words/starter.py", "")
write("exercises/review-count-words/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-count-words/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints 2 2 1 4."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_other_text():
    """An empty text has no words; a repeated word is counted every time."""
    count_words = function("count_words")
    assert count_words("") == {{}}
    assert count_words("a a a b") == {{"a": 3, "b": 1}}
''',
)
write(
    "exercises/review-count-words/wrong/first-only.py",
    REVIEW_CODE_SOLUTION.replace("counts[word] = counts.get(word, 0) + 1", "counts[word] = 1"),
)
write(
    "exercises/review-count-words/wrong/typed-in.py",
    "def count_words(text):\n    return {'to': 2, 'be': 2, 'or': 1, 'not': 1}\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.dsa.arrays-and-hashing written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
