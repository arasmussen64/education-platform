"""Writes the topic ml.dsa.trees-and-heaps (Module 6's fifth topic). Run from
the repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in. The
binary search tree is built and searched iteratively, so a chain of 3,000
nodes can't hit the recursion limit. Files are written as bytes with LF
endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.dsa.trees-and-heaps")


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

EXAMPLE = '''import heapq
import random
from collections import deque


class Node:
    def __init__(self, value, children=()):
        self.value = value
        self.children = list(children)


tree = Node("root", [Node("a", [Node("a1"), Node("a2")]), Node("b"), Node("c", [Node("c1", [Node("c1x")])])])


def depth_first(node):
    """Visit the node, then each child's whole subtree: recursion."""
    order = [node.value]
    for child in node.children:
        order.extend(depth_first(child))
    return order


def breadth_first(node):
    """Visit level by level: a queue."""
    order = []
    queue = deque([node])
    while queue:
        current = queue.popleft()
        order.append(current.value)
        queue.extend(current.children)
    return order


def depth(node):
    return 1 + max((depth(child) for child in node.children), default=0)


print("depth-first:", depth_first(tree))
print("breadth-first:", breadth_first(tree))
print("depth:", depth(tree))


class BSTNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def bst_insert(root, value):
    """Walk down: smaller goes left, larger goes right; hang the new node where the walk falls off."""
    if root is None:
        return BSTNode(value)
    node = root
    while True:
        side = "left" if value < node.value else "right"
        if getattr(node, side) is None:
            setattr(node, side, BSTNode(value))
            return root
        node = getattr(node, side)


def bst_search(root, value, counter):
    node = root
    while node is not None:
        counter[0] += 1
        if value == node.value:
            return True
        node = node.left if value < node.value else node.right
    return False


values = list(range(1000))
random.Random(2).shuffle(values)
shuffled_root = None
for value in values:
    shuffled_root = bst_insert(shuffled_root, value)
sorted_root = None
for value in range(1000):
    sorted_root = bst_insert(sorted_root, value)
for name, root in (("shuffled", shuffled_root), ("sorted", sorted_root)):
    counter = [0]
    assert bst_search(root, 999, counter)
    print(name, "insert order: finding 999 took", counter[0], "comparisons")

rng = random.Random(3)
stream = [rng.randint(1, 1_000_000) for _ in range(10_000)]
heap = []
for value in stream:
    heapq.heappush(heap, value)
    if len(heap) > 5:
        heapq.heappop(heap)
print("top 5 of 10,000:", sorted(heap, reverse=True))
print("the heap list itself:", heap, "(smallest first; the rest is not sorted)")
print("heapq.nlargest agrees:", heapq.nlargest(5, stream) == sorted(heap, reverse=True))

decision_tree = ("petal_length", 2.5, ("petal_width", 1.7, "virginica", "versicolor"), "setosa")


def decide(tree, flower):
    """Walk from the root question to a leaf: a tuple asks a question, a string is the answer."""
    steps = 0
    while isinstance(tree, tuple):
        feature, threshold, if_greater, if_not = tree
        tree = if_greater if flower[feature] > threshold else if_not
        steps += 1
    return tree, steps


for flower in ({"petal_length": 1.4, "petal_width": 0.2}, {"petal_length": 4.7, "petal_width": 1.4}, {"petal_length": 5.9, "petal_width": 2.1}):
    print(flower, "->", decide(decision_tree, flower))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert EX[0] == "depth-first: ['root', 'a', 'a1', 'a2', 'b', 'c', 'c1', 'c1x']", EX[0]
assert EX[1] == "breadth-first: ['root', 'a', 'b', 'c', 'a1', 'a2', 'c1', 'c1x']", EX[1]
assert EX[2] == "depth: 4", EX[2]
SHUFFLED_STEPS = int(EX[3].split()[-2])
SORTED_STEPS = int(EX[4].split()[-2])
assert EX[3].startswith("shuffled insert order") and 8 <= SHUFFLED_STEPS <= 30, EX[3]
assert EX[4] == "sorted insert order: finding 999 took 1000 comparisons", EX[4]
TOP5 = eval(EX[5].split(":", 1)[1])
HEAP_LIST = eval(EX[6].split(":", 1)[1].split("(")[0])
assert len(TOP5) == 5 and TOP5 == sorted(TOP5, reverse=True) and HEAP_LIST != sorted(HEAP_LIST), (TOP5, HEAP_LIST)
assert EX[7] == "heapq.nlargest agrees: True", EX[7]
assert EX[8].endswith("-> ('setosa', 1)") and EX[9].endswith("-> ('versicolor', 2)") and EX[10].endswith("-> ('virginica', 2)"), EX[8:]
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_PREORDER = '''tree = {"v": 1, "kids": [{"v": 2, "kids": [{"v": 4, "kids": []}]}, {"v": 3, "kids": []}]}


def walk(node, seen):
    seen.append(node["v"])
    for kid in node["kids"]:
        walk(kid, seen)
    return seen


print(walk(tree, []))
'''
PREDICT_PREORDER_OUT = out(PREDICT_PREORDER)
assert PREDICT_PREORDER_OUT == "[1, 2, 4, 3]\n", PREDICT_PREORDER_OUT

REVIEW_HEAP = '''import heapq

heap = []
for value in (5, 1, 8, 3, 9, 2):
    heapq.heappush(heap, value)
print(heap[0], len(heap))
print([heapq.heappop(heap) for _ in range(3)])
print(heap[0])
'''
REVIEW_HEAP_OUT = out(REVIEW_HEAP)
assert REVIEW_HEAP_OUT == "1 6\n[1, 2, 3]\n5\n", REVIEW_HEAP_OUT

PREDICT_DECIDE = '''tree = ("age", 30, ("income", 50, "A", "B"), "C")


def decide(tree, record):
    while isinstance(tree, tuple):
        feature, threshold, if_greater, if_not = tree
        tree = if_greater if record[feature] > threshold else if_not
    return tree


print(decide(tree, {"age": 45, "income": 20}), decide(tree, {"age": 30, "income": 90}))
'''
PREDICT_DECIDE_OUT = out(PREDICT_DECIDE)
assert PREDICT_DECIDE_OUT == "B C\n", PREDICT_DECIDE_OUT

PARSONS_LINES = [
    "from collections import deque",
    'tree = {"a": ["b", "c"], "b": ["d"], "c": [], "d": []}',
    'queue = deque(["a"])',
    "order = []",
    "while queue:",
    "    node = queue.popleft()",
    "    order.append(node)",
    "    queue.extend(tree[node])",
    "print(order)",
]
assert out("\n".join(PARSONS_LINES) + "\n") == "['a', 'b', 'c', 'd']\n"
assert out("\n".join(PARSONS_LINES).replace("queue.popleft()", "queue.pop()") + "\n") == "['a', 'c', 'b', 'd']\n"

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def insert(root, value):
    if root is None:
        return Node(value)
    node = root
    while True:
        side = "left" if value < node.value else "right"
        if getattr(node, side) is None:
            setattr(node, side, Node(value))
            return root
        node = getattr(node, side)


def contains(root, value):
    """Walk down from the root: left if the value is smaller, right if it is larger."""
    node = root
    while node is not None:
        if value == node.value:
            return True
        node = node.left if value < node.value else node.right
    return False


root = None
for value in (50, 30, 70, 20, 40, 60, 80):
    root = insert(root, value)
print(contains(root, 60), contains(root, 65), contains(root, 20))
'''
FILL_STARTER = FILL_SOLUTION.replace("node = node.left if value < node.value else node.right", "node = ... if value < node.value else ...")
FILL_WRONG = FILL_SOLUTION.replace("node = node.left if value < node.value else node.right", "node = node.right if value < node.value else node.left")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "True False True\n", FILL_OUT
assert out(FILL_WRONG) != FILL_OUT

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''def size(node):
    """How many nodes a tree has: this one plus every child's subtree."""
    return 1 + sum(size(child) for child in node["children"])


def depth(node):
    """How many levels: 1 for a leaf, 1 more than the deepest child otherwise."""
    return 1 + max((depth(child) for child in node["children"]), default=0)


leaf = lambda value: {"value": value, "children": []}
tree = {"value": "root", "children": [{"value": "a", "children": [leaf("a1"), leaf("a2")]}, leaf("b"), {"value": "c", "children": [{"value": "c1", "children": [leaf("c1x")]}]}]}
print(size(tree), depth(tree))
print(size(leaf("only")), depth(leaf("only")))
'''
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "8 4\n1 1\n", WRITE_OUT
WRITE_WRONG = WRITE_SOLUTION.replace("return 1 + max((depth(child) for child in node[\"children\"]), default=0)", "return max((1 + depth(child) for child in node[\"children\"]), default=0)")
assert out(WRITE_WRONG) != WRITE_OUT

# --- the build ----------------------------------------------------------------------------------

BUILD_SOLUTION = '''import heapq


class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def bst_insert(root, value):
    """Insert into a binary search tree by walking down, not by recursion; returns the root."""
    if root is None:
        return Node(value)
    node = root
    while True:
        side = "left" if value < node.value else "right"
        if getattr(node, side) is None:
            setattr(node, side, Node(value))
            return root
        node = getattr(node, side)


def bst_contains(root, value):
    """Walk down comparing: left if smaller, right if larger."""
    node = root
    while node is not None:
        if value == node.value:
            return True
        node = node.left if value < node.value else node.right
    return False


def top_k(values, k):
    """The k largest values, largest first, keeping a heap of only k values."""
    heap = []
    for value in values:
        heapq.heappush(heap, value)
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted(heap, reverse=True)


def decide(tree, record):
    """A decision tree as nested tuples (feature, threshold, if_greater, if_not); a string is a leaf."""
    while isinstance(tree, tuple):
        feature, threshold, if_greater, if_not = tree
        tree = if_greater if record[feature] > threshold else if_not
    return tree


root = None
for value in (50, 30, 70, 20, 40, 60, 80):
    root = bst_insert(root, value)
print(bst_contains(root, 60), bst_contains(root, 65))
print(top_k([5, 1, 8, 3, 9, 2, 8], 3))
tree = ("petal_length", 2.5, ("petal_width", 1.7, "virginica", "versicolor"), "setosa")
print(decide(tree, {"petal_length": 4.7, "petal_width": 1.4}), decide(tree, {"petal_length": 1.0, "petal_width": 0.1}))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == "True False\n[9, 8, 8]\nversicolor setosa\n", BUILD_OUT
BUILD_RECURSIVE_INSERT = BUILD_SOLUTION.replace(
    '''    if root is None:
        return Node(value)
    node = root
    while True:
        side = "left" if value < node.value else "right"
        if getattr(node, side) is None:
            setattr(node, side, Node(value))
            return root
        node = getattr(node, side)''',
    '''    if root is None:
        return Node(value)
    if value < root.value:
        root.left = bst_insert(root.left, value)
    else:
        root.right = bst_insert(root.right, value)
    return root''',
)
BUILD_TOP_K_SORTS = BUILD_SOLUTION.replace(
    '''    heap = []
    for value in values:
        heapq.heappush(heap, value)
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted(heap, reverse=True)''',
    "    return sorted(values, reverse=True)[:k]",
)
BUILD_DECIDE_SWAPPED = BUILD_SOLUTION.replace("tree = if_greater if record[feature] > threshold else if_not", "tree = if_not if record[feature] > threshold else if_greater")
assert out(BUILD_RECURSIVE_INSERT) == BUILD_OUT and out(BUILD_TOP_K_SORTS) == BUILD_OUT and out(BUILD_DECIDE_SWAPPED) != BUILD_OUT

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
'''

# The top-k budget sits between the heap's count and a full sort's, with room on both sides.
PROBE = '''import heapq
import random
''' + TRACKED + '''

rng = random.Random(5)
stream = [rng.randint(1, 10**9) for _ in range(20_000)]


def heap_top_k(values, k):
    heap = []
    for value in values:
        heapq.heappush(heap, value)
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted(heap, reverse=True)


Tracked.compared = 0
heap_top_k(tracked(stream), 5)
heap_count = Tracked.compared
Tracked.compared = 0
sorted(tracked(stream), reverse=True)[:5]
print(heap_count, Tracked.compared)
'''
HEAP_COUNT, SORT_COUNT = (int(v) for v in out(PROBE).split())
print("top-k probe: heap", HEAP_COUNT, "sort", SORT_COUNT)
TOP_K_BUDGET = (HEAP_COUNT + SORT_COUNT) // 2
assert HEAP_COUNT < 0.75 * TOP_K_BUDGET and SORT_COUNT > 1.33 * TOP_K_BUDGET, (HEAP_COUNT, SORT_COUNT)

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''import heapq


def top_k(values, k):
    """The k largest values, largest first, keeping only k values in the heap at a time."""
    heap = []
    for value in values:
        heapq.heappush(heap, value)
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted(heap, reverse=True)


readings = [12, 95, 3, 88, 41, 95, 7, 66, 23, 50]
print(top_k(readings, 3))
print(top_k(readings, 1), top_k(readings, 10))
'''
BUG_POP = ("            heapq.heappop(heap)", "            heap.pop()")
BUG_ORDER = ("    return sorted(heap, reverse=True)", "    return heap")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_POP).replace(*BUG_ORDER)
DEBUG_STILL_POP = DEBUG_SOLUTION.replace(*BUG_POP)
DEBUG_STILL_ORDER = DEBUG_SOLUTION.replace(*BUG_ORDER)
DEBUG_OUT = out(DEBUG_SOLUTION)
STILL_POP_OUT = out(DEBUG_STILL_POP)
STILL_ORDER_OUT = out(DEBUG_STILL_ORDER)
print("debug:\n" + DEBUG_OUT + "starter:\n" + out(DEBUG_STARTER) + "pop only:\n" + STILL_POP_OUT + "order only:\n" + STILL_ORDER_OUT)
assert DEBUG_OUT == "[95, 95, 88]\n[95] [95, 95, 88, 66, 50, 41, 23, 12, 7, 3]\n", DEBUG_OUT
assert STILL_POP_OUT != DEBUG_OUT and STILL_ORDER_OUT != DEBUG_OUT and out(DEBUG_STARTER) != DEBUG_OUT
STARTER_FIRST = out(DEBUG_STARTER).splitlines()[0]
ORDER_ONLY_FIRST = STILL_ORDER_OUT.splitlines()[0]

REVIEW_CODE_SOLUTION = '''def leaves(node):
    """How many nodes have no children: a leaf counts 1, any other node counts its children's leaves."""
    if not node["children"]:
        return 1
    return sum(leaves(child) for child in node["children"])


leaf = lambda value: {"value": value, "children": []}
tree = {"value": "root", "children": [{"value": "a", "children": [leaf("a1"), leaf("a2")]}, leaf("b"), {"value": "c", "children": [leaf("c1")]}]}
print(leaves(tree), leaves(leaf("only")))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "4 1\n", REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.dsa.trees-and-heaps
kind: topic
status: ready
title: "Trees and heaps"
summary: "Trees as nested nodes: traversals, binary search trees and what unbalances them, heaps and heapq for top-k and priority queues, and a decision tree as the tree a model can be."
prerequisites: [ml.dsa.stacks-queues-recursion]
estimated_minutes: 55
rev: 1
objectives:
  - "Build a tree from nodes with children, and traverse it depth-first and breadth-first."
  - "Insert into and search a binary search tree, and say why its cost is log n when balanced and n when not."
  - "Keep the top k of a stream with a heap, and say what heapq guarantees and what it doesn't."
  - "Read a small decision tree as a tree of questions, and say why its depth is its cost."
# Linked, never copied or embedded: the Runestone book is CC BY-NC-SA 4.0;
# the Python documentation is under the PSF licence; Open Data Structures is
# CC BY 2.5.
resources:
  - title: "Problem Solving with Algorithms and Data Structures using Python (Brad Miller and David Ranum), chapter 7: Trees and Tree Algorithms, sections 7.2 and 7.3 (examples and vocabulary), 7.6 (traversals), 7.9 and 7.10 (binary heaps) and 7.13 (search tree implementation)"
    url: https://runestone.academy/ns/books/published/pythonds3/Trees/toctree.html
    type: reading
    use: link
    license: CC BY-NC-SA 4.0
  - title: "The Python documentation: heapq, the heap queue algorithm (the theory section explains the invariant)"
    url: https://docs.python.org/3/library/heapq.html
    type: reading
    use: link
    license: "PSF licence (linked, not copied)"
  - title: "Open Data Structures in Python (Pat Morin), chapter 6: Binary Trees, sections 6.1 and 6.2 (binary trees and binary search trees)"
    url: https://opendatastructures.org/ods-python/6_Binary_Trees.html
    type: reading
    use: link
    license: CC BY 2.5
practice:
  - example-trees-three-ways
  - predict-a-walk
  - parsons-level-by-level
  - mcq-a-tree-that-became-a-chain
  - mcq-what-a-heap-promises
  - mcq-top-k-of-a-stream
  - mcq-the-cost-of-a-prediction
  - predict-a-decision
  - fill-search-a-tree
  - write-size-and-depth
prove:
  build: build-a-search-tree-and-a-heap
  debug: debug-top-k
  explain:
    prompt: |
      A teammate stores a million sorted customer ids in a binary search tree "so lookups are logarithmic", and finds them slower than a list scan; another keeps the 10 best scores of a day's million predictions by sorting the whole list every time; a third asks why a decision tree with 10,000 nodes predicts in a few steps. In your own words: what a tree is and the two ways to walk one; how a binary search tree finds a value and why inserting sorted data ruins it; how a heap keeps the top k of a stream cheaply and what the heap's list does and doesn't promise; and why a decision tree's prediction cost is its depth.
    rubric:
      - id: traverse
        required: true
        description: "A tree is nodes with children, one root, no cycles; depth-first visits a node then each child's whole subtree (recursion or an explicit stack), breadth-first visits level by level with a queue."
      - id: bst
        required: true
        description: "A binary search tree keeps smaller values left and larger right, so a search compares and goes one way, about log n steps when the tree is balanced; inserting already-sorted values hangs each new node under the last, a chain of depth n, and the search becomes a scan. Shuffle first, or use a self-balancing tree."
      - id: heap
        required: true
        description: "A min-heap of size k: push each value, pop the smallest when the heap exceeds k; what remains is the k largest, at about log k per element. heapq promises that heap[0] is the smallest and that push and pop keep that; it does not keep the list sorted."
      - id: decision-tree
        required: true
        description: "A decision tree is a tree of questions about the features; a prediction follows one path from the root to a leaf, so its cost is the depth (a few dozen questions at most), not the number of nodes."
    model_answer: |
      A tree is a set of nodes where one is the root and every other node has exactly one parent, so there are no cycles; a node's children are its subtrees. There are two natural ways to walk one. Depth-first visits a node and then each child's entire subtree before moving to the next child, which is a recursive function or a loop with an explicit stack. Breadth-first visits the root, then all of its children, then all of theirs, level by level, which is a loop with a queue. A binary search tree is a tree in which every node's left subtree holds smaller values and its right subtree larger ones, so finding a value is a walk from the root: compare, go left or right, repeat. If the tree is balanced, each step halves what is left and the walk takes about log n comparisons, twenty for a million. The teammate's tree was built by inserting ids that were already sorted, so each new id was larger than everything before it and hung off the right of the previous node: the tree is a chain a million nodes deep, and the search walks the whole chain, which is a scan with the overhead of following references. Shuffling the ids before inserting fixes it, and a self-balancing tree fixes it for good. For the top ten, a heap keeps the ten best as the stream goes by: push each score onto a min-heap, and when the heap holds eleven, pop the smallest. Each push and pop costs about log 10 comparisons, so a million scores cost a few million steps instead of a full sort each time. heapq promises that the first element of the list is always the smallest and that heappush and heappop keep that true; it does not promise that the rest of the list is in order, so the result has to be sorted at the end, which is cheap for ten items. A decision tree predicts by asking one question at the root, going to the yes or no child, and asking again until it reaches a leaf, so a prediction visits one path, whose length is the tree's depth. Ten thousand nodes can be a tree only a dozen levels deep, and a dozen questions is the cost; the size of the tree only matters for memory and for training.
review_pool:
  - review-predict-heap-pops
  - review-mcq-which-walk
  - review-mcq-a-million-in-a-balanced-tree
  - review-count-leaves
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: traverse
    description: "Build a tree from nodes with children, and walk it depth-first and breadth-first"
  - id: bst
    description: "Insert into and search a binary search tree, and say what balances and unbalances it"
  - id: heap
    description: "Keep the top k of a stream with a heap, and say what heapq promises"
  - id: decision-tree
    description: "Read a decision tree as a tree of questions, and say why its depth is its cost"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

A **tree** is the shape of anything nested: a file system, a company, a JSON document, a decision. This topic builds one from nodes with children and walks it two ways; then meets the two trees that algorithms lean on, the **binary search tree**, whose shape decides whether a search is 10 steps or 1,000, and the **heap**, which keeps the best few of a stream without sorting it; and ends with a **decision tree**, the first machine-learning model that is a data structure you can read.

The main resource is **_Problem Solving with Algorithms and Data Structures using Python_, chapter 7**: examples and vocabulary (7.2, 7.3), traversals (7.6), binary heaps (7.9, 7.10) and the search tree implementation (7.13); about 45 minutes. The `heapq` documentation's theory section is the clearest short account of the heap invariant. Watch for:

- **Parent, child, leaf, depth**: the vocabulary everything else uses.
- **Pre-order and level-order** are depth-first and breadth-first.
- **The heap invariant**: every parent is no larger than its children.

</Intro>

<Resource index={{0}} />

<Recap>

- **A tree** is nodes with children: one **root**, every other node with exactly one parent, no cycles; a node with no children is a **leaf**; the **depth** is the number of levels. In Python a node is a small class or a dict with a `children` list. **Depth-first** traversal visits a node, then each child's whole subtree (recursion, or the last topic's explicit stack): the example's order is root, a, a1, a2, b, c, c1, c1x. **Breadth-first** visits level by level with a queue: root, a, b, c, a1, a2, c1, c1x. Size and depth are recursive one-liners: 1 plus the sum, or the max, over the children.
- **A binary search tree** keeps every node's smaller values in its left subtree and larger ones in its right. Searching is a walk: compare, go left or right, repeat; inserting is the same walk until it falls off the tree, and the new node hangs there. When the tree is **balanced** (every level roughly full) the walk is about `log2 n` steps: {SHUFFLED_STEPS} comparisons to find 999 among 1,000 values inserted in shuffled order. When the values arrive **already sorted**, each hangs under the last and the tree is a chain: finding 999 takes 1,000 comparisons, a scan with extra overhead. Shuffle first, or use a self-balancing tree (AVL, red-black; databases use B-trees); Python has none built in because `dict` and a sorted list cover most needs.
- **A heap** (`heapq`) is a list arranged so that `heap[0]` is the smallest and every parent is no larger than its children; `heappush` and `heappop` keep that in about `log n` steps each. It is **not sorted**: the example's heap list reads {HEAP_LIST}. It is a **priority queue**: whatever is smallest comes out next (the next topic's shortest-path search runs on one).
- **Top k of a stream:** push each value onto a min-heap and pop the smallest whenever the heap holds more than `k`; what is left is the `k` largest, at about `log k` per value, with only `k` values in memory: the example's top 5 of 10,000 random numbers, which `heapq.nlargest` confirms. Sorting the whole stream costs `n log n` and holds all of it.
- **A decision tree** is a tree of questions about a record's features, with answers at the leaves: `petal_length > 2.5`? if not, setosa; if so, `petal_width > 1.7`? A prediction walks one path from the root to a leaf, so its cost is the **depth**, not the number of nodes: the example's three flowers are classified in 1, 2 and 2 questions. Learning the questions from data is a later module; reading the tree is this one.
- **In machine learning:** decision trees and the random forests and gradient-boosted trees built from them are the strongest models on tabular data; heaps keep the best candidates in beam search and the top-k results of a ranking; nearest-neighbour search uses k-d trees; and every nested configuration, JSON response and model definition is a tree you walk with the two traversals.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/predict-a-walk.yaml",
    f'''id: predict-a-walk
type: predict_output
rev: 1
prompt: |
  A tree of dicts, walked by a recursive function that records each node before its children. What does the program print?
code: |
{block(PREDICT_PREORDER)}expected_output: |
{block(PREDICT_PREORDER_OUT)}explanation: |
  Depth-first: the root (1), then its first child's whole subtree (2, then 2's child 4), and only then the second child (3). A breadth-first walk would give `[1, 2, 3, 4]`, level by level.
skills: [traverse]
''',
)

write(
    "recall/parsons-level-by-level.yaml",
    "id: parsons-level-by-level\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to walk the tree breadth-first, level by level, and print `['a', 'b', 'c', 'd']`. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("    node = queue.pop()")
    + "\nexplanation: |\n"
    + block("Breadth-first takes nodes from the front of the queue, so a node's children, added at the back, wait until the nodes already queued are done: a, then b and c, then d. The decoy's `pop()` takes from the back, which turns the queue into a stack and visits c before b: depth-first, in a different order.")
    + "skills: [traverse]\n",
)

mcq(
    "mcq-a-tree-that-became-a-chain",
    "A binary search tree was filled by inserting a million ids that were already in increasing order. Searching it is slower than scanning a list. Why, and what fixes it?",
    [
        "Each id was larger than the last, so it hung off the right of the previous node: a chain a million deep; shuffle first, or use a self-balancing tree",
        "A million ids is too many for a tree, which works only up to about ten thousand nodes before the references cost more than they save; use a dict instead",
        "Binary search trees are always slower than lists, because following a reference costs more than indexing an array, however the tree is shaped",
        "The ids were integers, and a binary search tree needs strings to compare; convert them first",
    ],
    0,
    "A search tree is only logarithmic when it is roughly balanced, and the insertion order decides its shape. Sorted input is the worst case: every insert walks to the bottom of the chain and extends it, and every search walks it too. Shuffling the input gives a tree about log n deep on average; a self-balancing tree guarantees it.",
    ["bst"],
)

mcq(
    "mcq-what-a-heap-promises",
    "After several `heapq.heappush` calls, `heap` is `[1, 3, 2, 7, 4]`. Which statement is right?",
    [
        "The list is sorted except for a bug: 2 should come before 3",
        "`heap[0]` is the smallest; the rest obeys only the rule that each parent is no larger than its children, so the list isn't sorted",
        "`heap[-1]` is the largest, because a heap keeps both ends in order",
        "Reading `heap` from front to back gives the values from smallest to largest, which is what the heap maintains after every push and pop",
    ],
    1,
    "A heap is a tree stored in a list: the children of index `i` are at `2i + 1` and `2i + 2`, and the only promise is that each parent is no larger than its children. So 1 is at the front, 3 and 2 are its children in either order, and 7 and 4 are 3's children. To get the values in order, pop them one at a time; to see the largest, keep a heap of negated values or use `heapq.nlargest`.",
    ["heap"],
)

mcq(
    "mcq-top-k-of-a-stream",
    "Ten million predictions arrive one at a time and the ten highest scores are wanted. Why does the recommended method use a min-heap of size ten, rather than a max-heap or a sort?",
    [
        "Because a min-heap is faster to build than a max-heap in Python",
        "Because the ten highest scores are the ten smallest negative scores, and `heapq` only handles minima",
        "Because sorting ten million values is impossible within Python's memory limits; a heap is the only structure that scales past a million values",
        "A min-heap of ten holds the ten best and evicts its smallest in `log 10` steps when a better score arrives; a sort costs `n log n`",
    ],
    3,
    "The question for each new score is \"is it better than the worst of my current ten?\", and the worst of ten is exactly what a min-heap of ten keeps at `heap[0]`. Pushing a score and popping the smallest costs about `log 10` comparisons, so the whole stream costs `n log k`, with ten values in memory, where a sort costs `n log n` and all of them. A max-heap would answer the wrong question cheaply. Sorting isn't impossible, just unnecessary.",
    ["heap"],
)

mcq(
    "mcq-the-cost-of-a-prediction",
    "A trained decision tree has 10,000 nodes. Roughly how many questions does one prediction ask, and why?",
    [
        "About 10,000, one per node, because the record has to be checked against every rule the tree has learned",
        "About 5,000, because on average half the nodes are visited",
        "A few dozen at most: the tree's depth, since a prediction walks one path from root to leaf",
        "Exactly 100, because a tree with 10,000 nodes is always a hundred levels deep",
    ],
    2,
    "Each question sends the record to one child, so a prediction visits one node per level and stops at a leaf: the cost is the depth, not the size. A tree of 10,000 nodes can be as shallow as 14 levels if balanced, and trained trees are usually limited to a depth of a few to a few dozen. Size matters for memory and training, depth for prediction.",
    ["decision-tree"],
)

write(
    "recall/predict-a-decision.yaml",
    f'''id: predict-a-decision
type: predict_output
rev: 1
prompt: |
  A decision tree as nested tuples: a question is `(feature, threshold, if_greater, if_not)`, asked as "is the record's feature greater than the threshold?", and a string is an answer. What does the program print for the two records?
code: |
{block(PREDICT_DECIDE)}expected_output: |
{block(PREDICT_DECIDE_OUT)}explanation: |
  The first record's age, 45, is greater than 30, so the walk takes the `if_greater` branch, the income question; 20 is not greater than 50, so the answer is `B`. The second record's age is exactly 30, which is not greater than 30, so it goes straight to the leaf `C` in one question. Each prediction follows one path, and a tie goes to the "not greater" side.
skills: [decision-tree]
''',
)

write(
    "recall/review-predict-heap-pops.yaml",
    f'''id: review-predict-heap-pops
type: predict_output
rev: 1
prompt: |
  Six values pushed onto a heap, then three popped. What does the program print?
code: |
{block(REVIEW_HEAP)}expected_output: |
{block(REVIEW_HEAP_OUT)}explanation: |
  `heap[0]` is always the smallest value in the heap, 1 of the six. Each `heappop` removes the smallest and repairs the heap, so the pops come out 1, 2, 3 in order, and the new smallest is 5. The heap gives values in order only through popping; the list itself is never sorted.
skills: [heap]
''',
)

mcq(
    "review-mcq-which-walk",
    "You want to print a directory tree with each folder's contents indented under it, and separately to find the shallowest file matching a name. Which traversal fits each?",
    [
        "Depth-first for both; breadth-first is only for graphs",
        "Depth-first for the listing (a folder, then everything inside it); breadth-first for the shallowest match (the first hit is the shallowest)",
        "Breadth-first for the listing, because folders at the same level belong together; depth-first for the search, because it reaches files faster",
        "Either works for both; the two walks visit the same nodes and differ only in speed",
    ],
    1,
    "An indented listing is a node followed by its whole subtree, which is depth-first in the order recursion produces. The shallowest match wants the levels visited in order, which is breadth-first with a queue: the first match found is the closest to the root. Both visit every node; they differ in order, and the order is the point.",
    ["traverse"],
)

mcq(
    "review-mcq-a-million-in-a-balanced-tree",
    "A balanced binary search tree holds a million values. About how many comparisons does a search take, and how does that compare with a sorted list and a dict?",
    [
        "About 20, like binary search on a sorted list; a dict is about 1 but keeps no order",
        "About 1,000, the square root of a million, like a sorted list; a dict is the same",
        "About 20 for the tree, about 1,000 for a sorted list, and about 1 for a dict",
        "About a million for the tree, since every node may need checking; a sorted list is 20 and a dict 1",
    ],
    0,
    "Each comparison in a balanced tree halves what remains, exactly as binary search halves a sorted list: `log2` of a million is about 20. A dict gives constant-time exact lookups but no order; the tree's advantage over the sorted list is cheap insertion in the middle, which a list pays for with a shift.",
    ["bst"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-trees-three-ways/exercise.yaml",
    f'''id: example-trees-three-ways
stage: worked_example
rev: 1
title: "Trees, three ways"
prompt: |
  A tree of nodes walked two ways, a binary search tree built in two orders, a heap keeping the top five of a stream, and a decision tree that classifies flowers. Press **Run**, then read how each part works.
steps:
  - label: "A tree of nodes"
    lines: "{ln('class Node')}-{ln('tree = Node(')}"
    note: "A node is a value and a list of children. The tree has a root with three children; `a` has two leaves, `b` is a leaf, and `c` has a child with a child. Depth 4."
  - label: "Depth-first, by recursion"
    lines: "{ln('def depth_first')}-{ln('    return order')}"
    note: "Visit the node, then each child's entire subtree before the next child: root, a, a1, a2, b, c, c1, c1x. The recursion is the last topic's; the call stack remembers which child comes next."
  - label: "Breadth-first, by queue"
    lines: "{ln('def breadth_first')}-{ln('    return order', ln('def breadth_first'))}"
    note: "Take a node from the front of a queue, record it, and put its children at the back: the root, then all of level two (a, b, c), then level three (a1, a2, c1), then c1x. The queue is what makes it level by level."
  - label: "Depth, and the three prints"
    lines: "{ln('def depth(node)')}-{ln('"depth:"')}"
    note: "Depth is 1 plus the deepest child, with `default=0` so a leaf is 1. The two orders differ exactly where a node has grandchildren."
  - label: "A binary search tree"
    lines: "{ln('class BSTNode')}-{ln('    return False')}"
    note: "Each node has a left and a right child. `bst_insert` walks down, left for smaller and right for larger, until the side it wants is empty, and hangs the new node there; `bst_search` walks the same way and counts its comparisons. Both are loops, not recursion, so a deep chain can't hit the recursion limit."
  - label: "Shuffled against sorted"
    lines: "{ln('values = list(range(1000))')}-{ln('insert order: finding')}"
    note: "The same thousand values inserted in a shuffled order and in sorted order. Finding 999 takes {SHUFFLED_STEPS} comparisons in the first tree, about `log2` of a thousand, and 1,000 in the second: sorted input hangs every node under the last, and the tree is a chain. The structure is the same; the shape decides the cost."
  - label: "Top five of a stream, with a heap"
    lines: "{ln('rng = random.Random(3)')}-{ln('heapq.nlargest agrees')}"
    note: "Ten thousand random numbers arrive one at a time. Each is pushed onto a min-heap; when the heap holds six, the smallest is popped, so the heap always holds the five largest seen. The heap list itself reads {HEAP_LIST}: smallest first, the rest not sorted, which is all a heap promises. `heapq.nlargest` on the whole stream agrees."
  - label: "A decision tree"
    lines: "{ln('decision_tree = (')}-{ln('    print(flower, ')}"
    note: "A question is a tuple: a feature, a threshold, the subtree if the feature is greater, and the subtree if not; a leaf is the answer. `decide` walks from the root to a leaf, counting questions: a short petal is setosa after one question, the others take two. The cost is the depth, however many nodes the tree has."
''',
)
write("exercises/example-trees-three-ways/solution.py", EXAMPLE)
write(
    "exercises/example-trees-three-ways/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the two walks and the depth, the two search counts, the top five and the heap list, and the three flowers."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-search-a-tree/exercise.yaml",
    f'''id: fill-search-a-tree
stage: fill_in
rev: 1
title: "Search a tree"
prompt: |
  `contains(root, value)` should walk down a binary search tree: at each node, stop if the value matches, otherwise go to the left child if the value is smaller and to the right child if it is larger. Replace each `...` so the program prints whether 60, 65 and 20 are in the tree:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "Smaller values live in the left subtree: when `value < node.value`, the next node is `node.left`."
  - "Otherwise the next node is `node.right`; when that is `None`, the walk has fallen off the tree and the value isn't there."
skills: [bst]
''',
)
write("exercises/fill-search-a-tree/starter.py", FILL_STARTER)
write("exercises/fill-search-a-tree/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-search-a-tree/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints True False True."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_every_value_and_some_gaps():
    """Every inserted value is found, values between them are not, and an empty tree holds nothing."""
    insert = function("insert")
    contains = function("contains")
    root = None
    for value in (8, 3, 10, 1, 6, 14, 4, 7, 13):
        root = insert(root, value)
    assert all(contains(root, value) for value in (8, 3, 10, 1, 6, 14, 4, 7, 13))
    assert not any(contains(root, value) for value in (0, 2, 5, 9, 11, 12, 15))
    assert not contains(None, 1)
''',
)
write("exercises/fill-search-a-tree/wrong/goes-the-wrong-way.py", FILL_WRONG)
write(
    "exercises/fill-search-a-tree/wrong/typed-in.py",
    FILL_SOLUTION.split("def contains")[0] + "def contains(root, value):\n    return value in (60, 20)\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-size-and-depth/exercise.yaml",
    f'''id: write-size-and-depth
stage: write
rev: 1
title: "Size and depth"
prompt: |
  A tree is a dict with a `value` and a list of `children` dicts. Write `size(node)`, the number of nodes in the tree (this one plus every child's subtree), and `depth(node)`, the number of levels (1 for a leaf, 1 more than the deepest child otherwise), both by recursion. Then print them for the starter's tree and for a single leaf:

  ```python
  print(size(tree), depth(tree))
  print(size(leaf("only")), depth(leaf("only")))
  ```

  ```
{block(WRITE_OUT)}  ```
hints:
  - "`1 + sum(size(child) for child in node[\\"children\\"])` counts this node and every subtree."
  - "`max(..., default=0)` handles a node with no children, so a leaf has depth 1."
skills: [traverse]
''',
)
write("exercises/write-size-and-depth/starter.py", "".join(line + "\n" for line in WRITE_SOLUTION.splitlines() if line.startswith(("leaf = ", "tree = "))))
write("exercises/write-size-and-depth/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-size-and-depth/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints 8 4 and 1 1."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_a_chain_and_a_star():
    """A chain of 200 nodes has size 200 and depth 200; a root with 1,000 leaves has size 1,001 and depth 2."""
    size = function("size")
    depth = function("depth")
    chain = {{"value": 0, "children": []}}
    for i in range(1, 200):
        chain = {{"value": i, "children": [chain]}}
    assert (size(chain), depth(chain)) == (200, 200)
    star = {{"value": "root", "children": [{{"value": i, "children": []}} for i in range(1000)]}}
    assert (size(star), depth(star)) == (1001, 2)
''',
)
write("exercises/write-size-and-depth/wrong/leaf-depth-zero.py", WRITE_WRONG)
write(
    "exercises/write-size-and-depth/wrong/typed-in.py",
    "def size(node):\n    return 8\n\n\ndef depth(node):\n    return 4\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-a-search-tree-and-a-heap/exercise.yaml",
    f'''id: build-a-search-tree-and-a-heap
stage: build
rev: 1
title: "A search tree and a heap"
prompt: |
  Starting from a blank editor, write a `Node` class with `value`, `left` and `right`, and four functions:

  - `bst_insert(root, value)`: insert into a binary search tree (smaller left, larger or equal right) by **walking down with a loop**, not by recursion, and return the root (a new node when `root` is `None`).
  - `bst_contains(root, value)`: whether the value is in the tree, by the same walk.
  - `top_k(values, k)`: the `k` largest values, largest first, using a heap that never holds more than `k` values (`heapq`).
  - `decide(tree, record)`: the leaf a decision tree reaches for a record; a question is a tuple `(feature, threshold, if_greater, if_not)`, taken as `record[feature] > threshold`, and a leaf is a string.

  Then print:

  ```python
  root = None
  for value in (50, 30, 70, 20, 40, 60, 80):
      root = bst_insert(root, value)
  print(bst_contains(root, 60), bst_contains(root, 65))
  print(top_k([5, 1, 8, 3, 9, 2, 8], 3))
  tree = ("petal_length", 2.5, ("petal_width", 1.7, "virginica", "versicolor"), "setosa")
  print(decide(tree, {{"petal_length": 4.7, "petal_width": 1.4}}), decide(tree, {{"petal_length": 1.0, "petal_width": 0.1}}))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks insert 3,000 values in sorted order (a chain that recursion can't walk), count the comparisons of a search in a shuffled tree (fewer than 100), and count the comparisons `top_k` makes on 20,000 values (fewer than {TOP_K_BUDGET:,}; sorting them all makes about {SORT_COUNT:,}).
skills: [bst, heap, decision-tree]
''',
)
write("exercises/build-a-search-tree-and-a-heap/starter.py", "")
write("exercises/build-a-search-tree-and-a-heap/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-a-search-tree-and-a-heap/test_exercise.py",
    f'''import random

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).
{TRACKED}

def test_the_output():
    """Prints the three lines."""
    assert run() == {BUILD_OUT!r}


def test_a_sorted_chain_of_three_thousand():
    """3,000 values inserted in sorted order are all found, and a missing one is not."""
    bst_insert = function("bst_insert")
    bst_contains = function("bst_contains")
    root = None
    for value in range(3000):
        root = bst_insert(root, value)
    assert bst_contains(root, 2999) and bst_contains(root, 0) and not bst_contains(root, 3000)


def test_a_shuffled_tree_searches_quickly():
    """In a tree of 3,000 shuffled values, finding one takes fewer than 100 comparisons."""
    bst_insert = function("bst_insert")
    bst_contains = function("bst_contains")
    values = list(range(3000))
    random.Random(6).shuffle(values)
    root = None
    for value in tracked(values):
        root = bst_insert(root, value)
    Tracked.compared = 0
    assert bst_contains(root, Tracked(2999)) and not bst_contains(root, Tracked(-1))
    assert Tracked.compared < 100


def test_top_k_keeps_a_small_heap():
    """The 5 largest of 20,000 values are right, found with fewer than {TOP_K_BUDGET:,} comparisons."""
    top_k = function("top_k")
    rng = random.Random(5)
    stream = [rng.randint(1, 10**9) for _ in range(20_000)]
    Tracked.compared = 0
    result = top_k(tracked(stream), 5)
    assert [item.value for item in result] == sorted(stream, reverse=True)[:5]
    assert Tracked.compared < {TOP_K_BUDGET}


def test_decide():
    """A three-level tree classifies four records."""
    decide = function("decide")
    tree = ("age", 30, ("income", 50, "A", "B"), ("income", 20, "C", "D"))
    records = [{{"age": 40, "income": 60}}, {{"age": 40, "income": 10}}, {{"age": 20, "income": 25}}, {{"age": 20, "income": 5}}]
    assert [decide(tree, record) for record in records] == ["A", "B", "C", "D"]
''',
)
write("exercises/build-a-search-tree-and-a-heap/wrong/recursive-insert.py", BUILD_RECURSIVE_INSERT)
write("exercises/build-a-search-tree-and-a-heap/wrong/top-k-sorts-everything.py", BUILD_TOP_K_SORTS)
write("exercises/build-a-search-tree-and-a-heap/wrong/decide-swapped.py", BUILD_DECIDE_SWAPPED)
write(
    "exercises/build-a-search-tree-and-a-heap/wrong/typed-in.py",
    "class Node:\n    def __init__(self, value):\n        self.value = value\n        self.left = None\n        self.right = None\n\n\ndef bst_insert(root, value):\n    return Node(value)\n\n\ndef bst_contains(root, value):\n    return value == 60\n\n\ndef top_k(values, k):\n    return [9, 8, 8]\n\n\ndef decide(tree, record):\n    return 'setosa'\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-top-k/exercise.yaml",
    f'''id: debug-top-k
stage: debug
rev: 1
title: "Top k, wrongly"
prompt: |
  `top_k(values, k)` should return the `k` largest readings, largest first, using a heap that never holds more than `k` values. The program should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the top three come out as `{STARTER_FIRST}`, because when the heap grows past `k` the program removes the **last element of the list** with `heap.pop()`, not the smallest; a heap's smallest is `heap[0]`, and only `heapq.heappop` removes it and repairs the heap. Fix that, and the right values appear in the wrong order, `{ORDER_ONLY_FIRST}`: the heap list is not sorted, so the result must be sorted before it is returned.
skills: [heap]
''',
)
write("exercises/debug-top-k/starter.py", DEBUG_STARTER)
write("exercises/debug-top-k/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-top-k/test_exercise.py",
    f'''from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the top three, the top one and all ten in order."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_other_streams():
    """The two largest of a longer stream come out largest first, and k above the length returns everything sorted."""
    top_k = function("top_k")
    assert top_k([4, 9, 1, 7, 9, 3, 8, 2, 6, 5, 0], 2) == [9, 9]
    assert top_k([3, 1, 2], 5) == [3, 2, 1]
''',
)
write("exercises/debug-top-k/wrong/still-pops-the-end.py", DEBUG_STILL_POP)
write("exercises/debug-top-k/wrong/still-unsorted.py", DEBUG_STILL_ORDER)
write(
    "exercises/debug-top-k/wrong/typed-in.py",
    "def top_k(values, k):\n    return [95, 95, 88]\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-count-leaves/exercise.yaml",
    f'''id: review-count-leaves
stage: review_code
rev: 1
title: "Count the leaves, from memory"
prompt: |
  A tree is a dict with a `value` and a list of `children`. Write `leaves(node)`, the number of nodes with no children, by recursion, and print it for the starter's tree and for a single leaf:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [traverse]
''',
)
write("exercises/review-count-leaves/starter.py", "".join(line + "\n" for line in REVIEW_CODE_SOLUTION.splitlines() if line.startswith(("leaf = ", "tree = "))))
write("exercises/review-count-leaves/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-count-leaves/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints 4 1."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_a_chain_and_a_star():
    """A chain has one leaf; a root with 50 children has 50."""
    leaves = function("leaves")
    chain = {{"value": 0, "children": []}}
    for i in range(1, 30):
        chain = {{"value": i, "children": [chain]}}
    assert leaves(chain) == 1
    assert leaves({{"value": "r", "children": [{{"value": i, "children": []}} for i in range(50)]}}) == 50
''',
)
write(
    "exercises/review-count-leaves/wrong/counts-every-node.py",
    REVIEW_CODE_SOLUTION.replace("    return sum(leaves(child) for child in node[\"children\"])", "    return 1 + sum(leaves(child) for child in node[\"children\"])"),
)
write(
    "exercises/review-count-leaves/wrong/typed-in.py",
    "def leaves(node):\n    return 4\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.dsa.trees-and-heaps written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
