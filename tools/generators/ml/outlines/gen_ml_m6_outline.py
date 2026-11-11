"""Outlines Module 6 of the ML Foundations track, data structures and
algorithms: planned topic.yaml files, the module in the track file, and the
spec's prose bullet turned into a table. Run from the repository root under uv.
Never overwrites a topic that isn't a planned outline."""

import pathlib

import yaml

ROOT = pathlib.Path(".")
TOPICS = ROOT / "content" / "topics"
TRACK_PATH = ROOT / "content" / "tracks" / "ml-foundations.yaml"
SPEC = ROOT / "docs" / "specs" / "ml-foundations.md"

MODULE = {
    "id": "ml.m6",
    "title": "Data structures and algorithms",
    "topics": [
        "ml.dsa.complexity",
        "ml.dsa.arrays-and-hashing",
        "ml.dsa.stacks-queues-recursion",
        "ml.dsa.sorting-and-searching",
        "ml.dsa.trees-and-heaps",
        "ml.dsa.graphs",
        "ml.dsa.dynamic-programming",
    ],
    "checkpoint": "ml.m6.checkpoint",
}

# id: (kind, title, summary, prerequisites, minutes, objectives, "you'll be able to" for the spec)
OUTLINES = {
    "ml.dsa.complexity": (
        "topic", "Counting steps and big-O",
        "How running time grows with the input: counting a function's operations, timing it as its input doubles, the common orders from constant to quadratic, and what a NumPy constant factor does and doesn't change.",
        ["ml.m2.checkpoint"], 50,
        ["Count the operations a function performs as a function of its input size, and name the order: O(1), O(log n), O(n), O(n log n), O(n²).",
         "Time a function as its input doubles, and read the growth off the timings.",
         "Predict which of two approaches scales, and say when the slower order is fine.",
         "Say what a NumPy vectorized operation changes (the constant) and what it doesn't (the order)."],
        "count a function's operations and name its order of growth; time a function as its input doubles and read the growth; predict which of two approaches scales and say when the slower one is fine; say what vectorizing with NumPy changes and what it doesn't"),
    "ml.dsa.arrays-and-hashing": (
        "topic", "Arrays, hash tables and sets",
        "What a list, a dict and a set cost per operation and why: contiguous arrays, amortized appends, hash functions and buckets; and the patterns they make fast: counting, deduplicating, grouping and joining.",
        ["ml.dsa.complexity"], 55,
        ["Say what indexing, appending, inserting at the front and searching a list cost, and why an array makes them so.",
         "Explain how a hash table turns a key into a bucket, what a collision is, and why dict and set lookups are constant time on average.",
         "Replace a nested-loop search with a dict or a set, and measure the difference.",
         "Count frequencies, deduplicate, group by key and join two tables with dictionaries."],
        "say what each list operation costs and why; explain how a hash table finds a key and why dict and set lookups are constant time on average; replace a quadratic search with a dict or a set and measure it; count, deduplicate, group and join with dictionaries"),
    "ml.dsa.stacks-queues-recursion": (
        "topic", "Stacks, queues and recursion",
        "Last-in-first-out and first-in-first-out as structures: a stack on a list, a queue on a deque, why popping from the front of a list is slow, and recursion as a stack the interpreter keeps for you.",
        ["ml.dsa.arrays-and-hashing"], 50,
        ["Use a list as a stack and a deque as a queue, and say why list.pop(0) is the wrong queue.",
         "Match brackets, evaluate postfix arithmetic and undo actions with a stack.",
         "Write a recursive function, trace its call stack, and turn it into a loop with an explicit stack.",
         "Say what a linked list is, why Python rarely needs one, and where the idea still appears."],
        "use a list as a stack and a deque as a queue, and say why popping from the front of a list is slow; solve bracket matching and undo with a stack; write and trace a recursive function and turn it into a loop with an explicit stack; say what a linked list is and where the idea appears"),
    "ml.dsa.sorting-and-searching": (
        "topic", "Sorting and searching",
        "Binary search on sorted data, insertion sort and merge sort written and timed, why n log n is the floor for sorting by comparisons, Python's sorted with keys, and NumPy's argsort.",
        ["ml.dsa.stacks-queues-recursion"], 55,
        ["Write binary search, and say why it needs sorted data and takes log n steps.",
         "Write insertion sort and merge sort, and time them to see n² against n log n.",
         "Sort by a key and by several keys with sorted, and say why Python's sort being stable matters.",
         "Use np.argsort to order one array by another, and bisect to search a sorted list."],
        "write binary search and say why it takes log n steps; write insertion sort and merge sort and time n² against n log n; sort by one or several keys and say why a stable sort matters; order one array by another with argsort and search a sorted list with bisect"),
    "ml.dsa.trees-and-heaps": (
        "topic", "Trees and heaps",
        "Trees as nested nodes: traversals, binary search trees and what unbalances them, heaps and heapq for top-k and priority queues, and a decision tree as the tree a model can be.",
        ["ml.dsa.stacks-queues-recursion"], 55,
        ["Build a tree from nodes with children, and traverse it depth-first and breadth-first.",
         "Insert into and search a binary search tree, and say why its cost is log n when balanced and n when not.",
         "Keep the top k of a stream with a heap, and say what heapq guarantees and what it doesn't.",
         "Read a small decision tree as a tree of questions, and say why its depth is its cost."],
        "build and traverse a tree depth-first and breadth-first; insert into and search a binary search tree and say when it degrades; keep the top k of a stream with a heap; read a decision tree as a tree of questions"),
    "ml.dsa.graphs": (
        "topic", "Graphs",
        "Graphs as adjacency lists: breadth-first and depth-first search, shortest paths in hops and with Dijkstra's algorithm, and topological order, which is the order a computation graph runs in and backpropagation walks backwards.",
        ["ml.dsa.trees-and-heaps"], 60,
        ["Represent a graph as a dict of adjacency lists, directed or not, weighted or not.",
         "Find what is reachable and the shortest path in hops with breadth-first search, and detect a cycle with depth-first search.",
         "Find the cheapest path with Dijkstra's algorithm and a heap.",
         "Order a directed acyclic graph topologically, and say why a computation graph and a data pipeline both need that order."],
        "represent a graph as adjacency lists; find reachability and shortest paths in hops with breadth-first search and detect a cycle with depth-first search; find the cheapest path with Dijkstra's algorithm; order a directed acyclic graph topologically and say why computation graphs and pipelines need it"),
    "ml.dsa.dynamic-programming": (
        "topic", "Dynamic programming",
        "Problems whose answer is built from the answers to smaller versions: memoization with a dict and with lru_cache, tables filled bottom-up, and three classics, Fibonacci, the edit distance between two strings, and the knapsack.",
        ["ml.dsa.stacks-queues-recursion", "ml.dsa.arrays-and-hashing"], 60,
        ["Spot overlapping subproblems, and say why plain recursion repeats work exponentially.",
         "Memoize a recursive function with a dict and with functools.lru_cache, and count the calls saved.",
         "Fill a table bottom-up for the edit distance between two strings, and read the edits back out of it.",
         "Solve the knapsack problem with a table, and say what makes a problem a dynamic-programming problem."],
        "spot overlapping subproblems and say why plain recursion repeats work; memoize with a dict and with lru_cache and count the calls saved; compute the edit distance between two strings bottom-up and read the edits back; solve the knapsack with a table and say what makes a problem dynamic programming"),
    "ml.m6.checkpoint": (
        "checkpoint", "Checkpoint 6: the algorithms behind a pipeline",
        "A small data pipeline built from the module's tools: deduplicate and join records with hashing, keep the top k with a heap, match near-duplicate names by edit distance, and order the pipeline's steps by topological sort, each at the right cost.",
        ["ml.dsa.arrays-and-hashing", "ml.dsa.graphs", "ml.dsa.dynamic-programming"], 120,
        ["Build the pieces of a small data pipeline (deduplicate, join, top-k, near-duplicate matching, step ordering) and show by counting steps that each scales as its order of growth says.",
         "Find and fix three bugs that each make a step quadratic or wrong: a nested-loop lookup where a set belongs, a queue popped from the front of a list, and a table filled in the wrong order.",
         "Explain why a dictionary lookup is constant time on average, and what a topological order guarantees."],
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
if not any(module["id"] == "ml.m6" for module in track["modules"]):
    track["modules"].append(MODULE)
    TRACK_PATH.write_bytes(dump(track).encode("utf-8"))
    print("wrote", TRACK_PATH)
else:
    print("track already has ml.m6")

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
if "## Module 6: Data structures and algorithms" not in spec:
    rows = []
    for number, topic_id in enumerate(MODULE["topics"], start=36):
        kind, title, summary, prereqs, minutes, objectives, able = OUTLINES[topic_id]
        needs = ", ".join(f"`{p}`" for p in prereqs)
        rows.append(f"| {number} | {title} | `{topic_id}` | {needs} | {able} |")
    section = (
        "## Module 6: Data structures and algorithms\n\n"
        "Module 2 gave the learner Python; this module gives them the cost of what they write. Counting steps and timing as the input doubles; the structures Python hands over (lists, dicts, sets, deques, heaps) and what each costs; recursion; sorting and searching; trees, and graphs including the computation graph that backpropagation walks; dynamic programming; and a checkpoint that builds the algorithms behind a data pipeline. Every topic is proven in code. Timings appear in the worked examples, read as ratios; the checks count steps, because a browser and CI don't share a clock.\n\n"
        "| # | Topic | ID | Needs | You'll be able to… |\n"
        "| --- | --- | --- | --- | --- |\n"
        + "\n".join(rows)
        + "\n\n"
        "**Checkpoint 6: the algorithms behind a pipeline** (`ml.m6.checkpoint`). Build the pieces of a small data pipeline from the module's tools: deduplicate and join records with hashing, keep the top k with a heap, match near-duplicate names by edit distance, and order the pipeline's steps by topological sort, each shown by counting steps to scale as its order says; debug three bugs that each make a step quadratic or wrong (a nested-loop lookup where a set belongs, a queue popped from the front of a list, a table filled in the wrong order); explain why a dictionary lookup is constant time on average and what a topological order guarantees. The way through for a stuck learner, as in the earlier checkpoints: a solved sibling, steps, fresh versions.\n\n"
    )
    old_bullet = "- **6. Data structures and algorithms:** complexity; arrays, hashing, trees, graphs; sorting and searching; dynamic programming; the algorithms behind data pipelines.\n"
    assert old_bullet in spec, "the Module 6 prose bullet has changed"
    spec = spec.replace(old_bullet, "")
    old_sentence = "as Modules 3 to 5 had before they were written (all three on 2026-11-10)."
    assert old_sentence in spec, "the later-modules sentence has changed"
    spec = spec.replace(
        old_sentence,
        "as Modules 3 to 5 had before they were written (all three on 2026-11-10) and Module 6 has (outlined 2026-11-10).",
    )
    assert spec.count("## Later modules") == 1
    spec = spec.replace("## Later modules", section + "## Later modules")
    SPEC.write_bytes(spec.encode("utf-8"))
    print("wrote", SPEC)
else:
    print("spec already has Module 6")
