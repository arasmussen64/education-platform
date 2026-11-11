"""Writes the topic ml.dsa.graphs (Module 6's sixth topic). Run from the
repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Graphs are dicts in insertion order, so every traversal prints the same in
both runtimes. Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.dsa.graphs")


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
from collections import deque

roads = [("A", "B", 4), ("A", "C", 2), ("B", "C", 5), ("B", "D", 10), ("C", "E", 3), ("E", "D", 4), ("D", "F", 11)]
graph = {}
for a, b, km in roads:
    graph.setdefault(a, {})[b] = km
    graph.setdefault(b, {})[a] = km
print("neighbours of C:", graph["C"])


def breadth_first(graph, start):
    """Hops from start to every reachable node, and each node's parent on a fewest-hops path."""
    hops = {start: 0}
    parent = {start: None}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbour in graph[node]:
            if neighbour not in hops:
                hops[neighbour] = hops[node] + 1
                parent[neighbour] = node
                queue.append(neighbour)
    return hops, parent


def path_to(parent, goal):
    """Walk the parent links back to the start, then reverse."""
    path = []
    while goal is not None:
        path.append(goal)
        goal = parent[goal]
    return path[::-1]


hops, parent = breadth_first(graph, "A")
print("hops from A:", hops)
print("fewest roads A to F:", path_to(parent, "F"))


def dijkstra(graph, start):
    """Cheapest distance from start to every node: always settle the closest unsettled node next."""
    distance = {start: 0}
    parent = {start: None}
    settled = set()
    heap = [(0, start)]
    while heap:
        cost, node = heapq.heappop(heap)
        if node in settled:
            continue
        settled.add(node)
        for neighbour, km in graph[node].items():
            if cost + km < distance.get(neighbour, float("inf")):
                distance[neighbour] = cost + km
                parent[neighbour] = node
                heapq.heappush(heap, (cost + km, neighbour))
    return distance, parent


distance, parent = dijkstra(graph, "A")
print("km from A:", distance)
print("cheapest A to F:", path_to(parent, "F"), "at", distance["F"], "km")

pipeline = {"load": ["clean"], "clean": ["features", "report"], "features": ["train"], "train": ["evaluate"], "report": [], "evaluate": []}


def topological_order(graph):
    """Kahn's algorithm: repeatedly take a node that nothing unfinished still points at."""
    indegree = {node: 0 for node in graph}
    for node in graph:
        for next_node in graph[node]:
            indegree[next_node] += 1
    ready = deque(node for node in graph if indegree[node] == 0)
    order = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for next_node in graph[node]:
            indegree[next_node] -= 1
            if indegree[next_node] == 0:
                ready.append(next_node)
    if len(order) < len(graph):
        raise ValueError("the graph has a cycle")
    return order


print("pipeline order:", topological_order(pipeline))
pipeline["evaluate"] = ["clean"]
try:
    topological_order(pipeline)
except ValueError as error:
    print("after evaluate -> clean:", error)

computation = {"x": ["times"], "w": ["times"], "times": ["plus"], "b": ["plus"], "plus": ["minus"], "y": ["minus"], "minus": ["square"], "square": []}
forward = topological_order(computation)
print("forward pass:", forward)
print("backward pass:", forward[::-1])
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert EX[0] == "neighbours of C: {'A': 2, 'B': 5, 'E': 3}", EX[0]
assert EX[1] == "hops from A: {'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 2, 'F': 3}", EX[1]
assert EX[2] == "fewest roads A to F: ['A', 'B', 'D', 'F']", EX[2]
assert EX[3] == "km from A: {'A': 0, 'B': 4, 'C': 2, 'E': 5, 'D': 9, 'F': 20}", EX[3]
assert EX[4] == "cheapest A to F: ['A', 'C', 'E', 'D', 'F'] at 20 km", EX[4]
assert EX[5] == "pipeline order: ['load', 'clean', 'features', 'report', 'train', 'evaluate']", EX[5]
assert EX[6] == "after evaluate -> clean: the graph has a cycle", EX[6]
assert EX[7] == "forward pass: ['x', 'w', 'b', 'y', 'times', 'plus', 'minus', 'square']", EX[7]
assert EX[8] == "backward pass: ['square', 'minus', 'plus', 'times', 'y', 'b', 'w', 'x']", EX[8]
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_ADJACENCY = '''edges = [("a", "b"), ("a", "c"), ("b", "c"), ("c", "d")]
graph = {}
for u, v in edges:
    graph.setdefault(u, []).append(v)
    graph.setdefault(v, []).append(u)
print(graph["c"], len(graph["a"]), len(graph["d"]))
'''
PREDICT_ADJACENCY_OUT = out(PREDICT_ADJACENCY)
assert PREDICT_ADJACENCY_OUT == "['a', 'b', 'd'] 2 1\n", PREDICT_ADJACENCY_OUT

PREDICT_TOPO = '''from collections import deque

graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
indegree = {node: 0 for node in graph}
for node in graph:
    for next_node in graph[node]:
        indegree[next_node] += 1
print(indegree)
ready = deque(node for node in graph if indegree[node] == 0)
order = []
while ready:
    node = ready.popleft()
    order.append(node)
    for next_node in graph[node]:
        indegree[next_node] -= 1
        if indegree[next_node] == 0:
            ready.append(next_node)
print(order)
'''
PREDICT_TOPO_OUT = out(PREDICT_TOPO)
assert PREDICT_TOPO_OUT == "{'a': 0, 'b': 1, 'c': 1, 'd': 2}\n['a', 'b', 'c', 'd']\n", PREDICT_TOPO_OUT

REVIEW_DIJKSTRA = '''import heapq

graph = {"A": {"B": 1, "C": 4}, "B": {"C": 2}, "C": {"D": 1}, "D": {}}
heap = [(0, "A")]
settled = []
while heap:
    cost, node = heapq.heappop(heap)
    if node in settled:
        continue
    settled.append(node)
    print("settled", node, "at", cost)
    for neighbour, weight in graph[node].items():
        heapq.heappush(heap, (cost + weight, neighbour))
'''
REVIEW_DIJKSTRA_OUT = out(REVIEW_DIJKSTRA)
assert REVIEW_DIJKSTRA_OUT == "settled A at 0\nsettled B at 1\nsettled C at 3\nsettled D at 4\n", REVIEW_DIJKSTRA_OUT

PARSONS_LINES = [
    "from collections import deque",
    'graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}',
    'hops = {"a": 0}',
    'queue = deque(["a"])',
    "while queue:",
    "    node = queue.popleft()",
    "    for neighbour in graph[node]:",
    "        if neighbour not in hops:",
    "            hops[neighbour] = hops[node] + 1",
    "            queue.append(neighbour)",
    "print(hops)",
]
assert out("\n".join(PARSONS_LINES) + "\n") == "{'a': 0, 'b': 1, 'c': 1, 'd': 2}\n"

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''from collections import deque


def fewest_hops_path(graph, start, goal):
    """A path from start to goal with the fewest edges, by breadth-first search with parent links."""
    parent = {start: None}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == goal:
            break
        for neighbour in graph[node]:
            if neighbour not in parent:
                parent[neighbour] = node
                queue.append(neighbour)
    if goal not in parent:
        return None
    path = []
    while goal is not None:
        path.append(goal)
        goal = parent[goal]
    return path[::-1]


metro = {"A": ["B", "C"], "B": ["A", "D"], "C": ["A", "D", "E"], "D": ["B", "C", "F"], "E": ["C"], "F": ["D"], "G": []}
print(fewest_hops_path(metro, "A", "F"))
print(fewest_hops_path(metro, "E", "B"))
print(fewest_hops_path(metro, "A", "G"))
'''
FILL_STARTER = FILL_SOLUTION.replace("                parent[neighbour] = node", "                parent[neighbour] = ...").replace("            if neighbour not in parent:", "            if neighbour not in ...:")
FILL_WRONG = FILL_SOLUTION.replace("        node = queue.popleft()", "        node = queue.pop()")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "['A', 'B', 'D', 'F']\n['E', 'C', 'A', 'B']\nNone\n", FILL_OUT
assert out(FILL_WRONG) != FILL_OUT

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''def has_cycle(graph):
    """Does a directed graph (a dict of lists) contain a cycle? Depth-first, remembering the nodes on the current path."""
    on_path = set()
    done = set()

    def visit(node):
        if node in on_path:
            return True
        if node in done:
            return False
        on_path.add(node)
        if any(visit(next_node) for next_node in graph[node]):
            return True
        on_path.remove(node)
        done.add(node)
        return False

    return any(visit(node) for node in graph)


print(has_cycle({"a": ["b"], "b": ["c"], "c": []}))
print(has_cycle({"a": ["b"], "b": ["c"], "c": ["a"]}))
print(has_cycle({"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}))
'''
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "False\nTrue\nFalse\n", WRITE_OUT
WRITE_WRONG = WRITE_SOLUTION.replace(
    '''        if node in on_path:
            return True
        if node in done:
            return False
        on_path.add(node)
        if any(visit(next_node) for next_node in graph[node]):
            return True
        on_path.remove(node)
        done.add(node)
        return False''',
    '''        if node in done:
            return True
        done.add(node)
        return any(visit(next_node) for next_node in graph[node])''',
)
assert out(WRITE_WRONG) != WRITE_OUT

# --- the build ----------------------------------------------------------------------------------

BUILD_SOLUTION = '''import heapq
from collections import deque


def shortest_hops(graph, start):
    """Hops from start to every reachable node, by breadth-first search."""
    hops = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbour in graph[node]:
            if neighbour not in hops:
                hops[neighbour] = hops[node] + 1
                queue.append(neighbour)
    return hops


def cheapest_path(graph, start, goal):
    """(cost, path) from start to goal in a weighted graph (dict of dicts), by Dijkstra's algorithm; None if unreachable."""
    distance = {start: 0}
    parent = {start: None}
    settled = set()
    heap = [(0, start)]
    while heap:
        cost, node = heapq.heappop(heap)
        if node in settled:
            continue
        settled.add(node)
        if node == goal:
            path = []
            while node is not None:
                path.append(node)
                node = parent[node]
            return cost, path[::-1]
        for neighbour, weight in graph[node].items():
            if cost + weight < distance.get(neighbour, float("inf")):
                distance[neighbour] = cost + weight
                parent[neighbour] = node
                heapq.heappush(heap, (cost + weight, neighbour))
    return None


def topological_order(graph):
    """An order in which every edge points forward (Kahn's algorithm); ValueError if the graph has a cycle."""
    indegree = {node: 0 for node in graph}
    for node in graph:
        for next_node in graph[node]:
            indegree[next_node] += 1
    ready = deque(node for node in graph if indegree[node] == 0)
    order = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for next_node in graph[node]:
            indegree[next_node] -= 1
            if indegree[next_node] == 0:
                ready.append(next_node)
    if len(order) < len(graph):
        raise ValueError("the graph has a cycle")
    return order


def has_cycle(graph):
    """True if topological_order can't place every node."""
    try:
        topological_order(graph)
    except ValueError:
        return True
    return False


roads = {"A": {"B": 4, "C": 2}, "B": {"A": 4, "C": 5, "D": 10}, "C": {"A": 2, "B": 5, "E": 3}, "D": {"B": 10, "E": 4, "F": 11}, "E": {"C": 3, "D": 4}, "F": {"D": 11}}
print(shortest_hops(roads, "A"))
print(cheapest_path(roads, "A", "F"))
pipeline = {"load": ["clean"], "clean": ["features", "report"], "features": ["train"], "train": ["evaluate"], "report": [], "evaluate": []}
print(topological_order(pipeline), has_cycle(pipeline))
print(has_cycle({"a": ["b"], "b": ["a"]}))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == (
    "{'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 2, 'F': 3}\n"
    "(20, ['A', 'C', 'E', 'D', 'F'])\n"
    "['load', 'clean', 'features', 'report', 'train', 'evaluate'] False\n"
    "True\n"
), BUILD_OUT
BUILD_DFS_HOPS = BUILD_SOLUTION.replace("        node = queue.popleft()\n        for neighbour in graph[node]:\n            if neighbour not in hops:", "        node = queue.pop()\n        for neighbour in graph[node]:\n            if neighbour not in hops:")
BUILD_GREEDY_PATH = BUILD_SOLUTION.replace("            if cost + weight < distance.get(neighbour, float(\"inf\")):", "            if neighbour not in distance:")
BUILD_TOPO_NO_CYCLE_CHECK = BUILD_SOLUTION.replace("    if len(order) < len(graph):\n        raise ValueError(\"the graph has a cycle\")\n    return order", "    return order")
for wrong in (BUILD_DFS_HOPS, BUILD_GREEDY_PATH, BUILD_TOPO_NO_CYCLE_CHECK):
    assert wrong != BUILD_SOLUTION and out(wrong) != BUILD_OUT

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''from collections import deque


def schedule(graph):
    """Steps in an order that respects every arrow, and whether every step was placed."""
    indegree = {node: 0 for node in graph}
    for node in graph:
        for next_node in graph[node]:
            indegree[next_node] += 1
    ready = deque(node for node in graph if indegree[node] == 0)
    order = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for next_node in graph[node]:
            indegree[next_node] -= 1
            if indegree[next_node] == 0:
                ready.append(next_node)
    return order, len(order) == len(graph)


pipeline = {"load": ["clean"], "clean": ["features", "report"], "features": ["train"], "train": ["evaluate"], "report": [], "evaluate": []}
order, complete = schedule(pipeline)
print(order, "complete" if complete else "stuck")
print(schedule({"a": ["b"], "b": ["c"], "c": ["a"]}))
'''
BUG_OUTDEGREE = ("            indegree[next_node] += 1", "            indegree[node] += 1")
BUG_NO_DECREMENT = ("            indegree[next_node] -= 1\n            if indegree[next_node] == 0:", "            if indegree[next_node] == 0:")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_OUTDEGREE).replace(*BUG_NO_DECREMENT)
DEBUG_STILL_OUTDEGREE = DEBUG_SOLUTION.replace(*BUG_OUTDEGREE)
DEBUG_STILL_NO_DECREMENT = DEBUG_SOLUTION.replace(*BUG_NO_DECREMENT)
DEBUG_OUT = out(DEBUG_SOLUTION)
STARTER_OUT = out(DEBUG_STARTER)
NO_DECREMENT_OUT = out(DEBUG_STILL_NO_DECREMENT)
print("debug:\n" + DEBUG_OUT + "starter:\n" + STARTER_OUT + "no decrement only:\n" + NO_DECREMENT_OUT)
assert DEBUG_OUT == "['load', 'clean', 'features', 'report', 'train', 'evaluate'] complete\n([], False)\n", DEBUG_OUT
assert STARTER_OUT.splitlines()[0] == "['report', 'evaluate'] stuck", STARTER_OUT
assert NO_DECREMENT_OUT.splitlines()[0] == "['load'] stuck", NO_DECREMENT_OUT
assert out(DEBUG_STILL_OUTDEGREE) != DEBUG_OUT

REVIEW_CODE_SOLUTION = '''from collections import deque


def reachable(graph, start):
    """Every node that can be reached from start, including start, as a set."""
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbour in graph[node]:
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append(neighbour)
    return seen


graph = {"a": ["b"], "b": ["c", "a"], "c": [], "d": ["a"]}
print(sorted(reachable(graph, "a")), sorted(reachable(graph, "d")), sorted(reachable(graph, "c")))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "['a', 'b', 'c'] ['a', 'b', 'c', 'd'] ['c']\n", REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.dsa.graphs
kind: topic
status: ready
title: "Graphs"
summary: "Graphs as adjacency lists: breadth-first and depth-first search, shortest paths in hops and with Dijkstra's algorithm, and topological order, which is the order a computation graph runs in and backpropagation walks backwards."
prerequisites: [ml.dsa.trees-and-heaps]
estimated_minutes: 60
rev: 1
objectives:
  - "Represent a graph as a dict of adjacency lists, directed or not, weighted or not."
  - "Find what is reachable and the shortest path in hops with breadth-first search, and detect a cycle with depth-first search."
  - "Find the cheapest path with Dijkstra's algorithm and a heap."
  - "Order a directed acyclic graph topologically, and say why a computation graph and a data pipeline both need that order."
# Linked, never copied or embedded: the Runestone book is CC BY-NC-SA 4.0;
# the Python documentation is under the PSF licence; Open Data Structures is
# CC BY 2.5.
resources:
  - title: "Problem Solving with Algorithms and Data Structures using Python (Brad Miller and David Ranum), chapter 8: Graphs and Graph Algorithms, sections 8.2 (vocabulary), 8.4 (adjacency lists), 8.6 and 8.7 (breadth-first search), 8.8 (depth-first search), 8.11 (topological sorting) and 8.13 (Dijkstra's algorithm)"
    url: https://runestone.academy/ns/books/published/pythonds3/Graphs/toctree.html
    type: reading
    use: link
    license: CC BY-NC-SA 4.0
  - title: "The Python documentation: graphlib.TopologicalSorter, topological order from the standard library"
    url: https://docs.python.org/3/library/graphlib.html
    type: reading
    use: link
    license: "PSF licence (linked, not copied)"
  - title: "Open Data Structures in Python (Pat Morin), chapter 12: Graphs, sections 12.1 to 12.3 (representations, breadth-first and depth-first traversal)"
    url: https://opendatastructures.org/ods-python/12_Graphs.html
    type: reading
    use: link
    license: CC BY 2.5
practice:
  - example-a-map-and-a-pipeline
  - predict-an-adjacency-list
  - parsons-hops-by-queue
  - mcq-fewest-edges
  - mcq-why-the-closest-first
  - predict-a-topological-order
  - mcq-no-order-means
  - mcq-the-backward-pass
  - fill-fewest-hops-path
  - write-has-cycle
prove:
  build: build-a-graph-toolkit
  debug: debug-a-scheduler
  explain:
    prompt: |
      A teammate stores a road network as a list of (from, to, km) triples and answers "how do I get from A to F" by trying every route; another runs a data pipeline's steps in the order they were written and gets "features not found" errors; a third asks why Module 4's backpropagation walked the layers backwards. In your own words: how you would store the network so that a node's neighbours are one lookup; how breadth-first search finds the fewest-roads route and why a visited set matters; how Dijkstra's algorithm finds the fewest-kilometres route and what a heap does for it; and what a topological order is, how to compute one, what it means when none exists, and why the forward pass and the backward pass of a network are the same order read two ways.
    rubric:
      - id: represent
        required: true
        description: "An adjacency list: a dict from each node to its neighbours (a list, or a dict of neighbour to weight), with both directions added for an undirected graph; memory proportional to nodes plus edges."
      - id: search
        required: true
        description: "Breadth-first search takes nodes from a queue in discovery order, so the first time a node is reached is along a fewest-edges path; parent links rebuild the path; the visited (or hops) set stops revisits and infinite loops. Depth-first search with a set of nodes on the current path finds cycles."
      - id: dijkstra
        required: true
        description: "Keep tentative distances; repeatedly settle the unsettled node with the smallest, relaxing its edges; a heap of (distance, node) makes picking the smallest cheap, about (V + E) log V overall; weights must not be negative."
      - id: topo
        required: true
        description: "A topological order lists nodes so every edge points forward; Kahn's algorithm takes nodes with no remaining incoming edges, decrementing in-degrees; nodes left over mean a cycle, which no order can satisfy. A computation graph's forward pass is a topological order and backpropagation visits the same nodes reversed, so each gradient is complete before it is used."
    model_answer: |
      I would store the network as a dict from each city to its neighbours, with the distance as the value: an adjacency list, built by adding each road in both directions. Then a city's neighbours are one lookup, and the whole thing takes memory proportional to the number of cities plus roads. The fewest-roads route is breadth-first search: start at A, put it in a queue, and repeatedly take the front city and add its unseen neighbours to the back, recording each one's parent. Because the queue hands out cities in the order they were discovered, every city is first reached along a path with the fewest edges, and following the parent links back from F gives that path. The visited set, or the hops dictionary, is what stops a city being added twice and stops the search looping forever around a circuit of roads. For the fewest kilometres, Dijkstra's algorithm keeps a tentative distance to every city and repeatedly settles the unsettled city with the smallest one, then checks whether going through it shortens the distance to each of its neighbours. A heap of (distance, city) pairs makes "the smallest unsettled" a cheap pop instead of a scan, so the whole thing costs about the number of roads times the logarithm of the number of cities; stale entries are skipped, and it needs road lengths that aren't negative. A topological order of the pipeline is a list of its steps in which every arrow points forward, so a step runs only after everything it depends on. Kahn's algorithm counts each step's incoming arrows, starts with the steps that have none, and each time a step runs decrements the counts of the steps it points at, releasing any that reach zero. If steps are left over when nothing is ready, the graph has a cycle, and no order can run it; the pipeline that failed was simply run in writing order instead of a topological one. A network's computation graph is the same kind of graph: each operation depends on its inputs, so the forward pass runs it in a topological order, and the backward pass walks exactly that order reversed, so that when a node's gradient is needed, every node that depends on it has already contributed. Module 4's layers formed a chain, where the topological order is just the layers in sequence and backpropagation is the sequence reversed.
review_pool:
  - review-predict-dijkstra-settles
  - review-mcq-list-or-matrix
  - review-mcq-looping-forever
  - review-reachable
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: represent
    description: "Represent a graph as a dict of adjacency lists, directed or not, weighted or not"
  - id: search
    description: "Find reachability and fewest-hops paths with breadth-first search, and cycles with depth-first search"
  - id: dijkstra
    description: "Find the cheapest path with Dijkstra's algorithm and a heap"
  - id: topo
    description: "Order a directed acyclic graph topologically, and say why computation graphs and pipelines need it"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

A **graph** is nodes joined by edges with no rule about shape: a road map, a social network, the steps of a data pipeline, the operations of a neural network. This topic stores one as a dict, walks it with the queue and the stack from two topics ago, finds the cheapest route with the heap from the last one, and ends with the order a pipeline's steps and a network's operations must run in, which is also the order backpropagation walks backwards. The worked example does all of that on a six-city road map and a six-step pipeline.

The main resource is **_Problem Solving with Algorithms and Data Structures using Python_, chapter 8**: vocabulary, adjacency lists, breadth-first and depth-first search, topological sorting and Dijkstra's algorithm; about 50 minutes, with the word-ladder and knight's-tour examples. The `graphlib` documentation shows the standard library's topological sorter. Watch for:

- **Vertex and edge, directed and weighted**: the vocabulary.
- **The visited set** is what stops a search from looping forever.
- **A topological order exists only when there is no cycle.**

</Intro>

<Resource index={{0}} />

<Recap>

- **A graph** is **nodes** (vertices) and **edges**; edges can be **directed** (one way) or not, and **weighted** (a cost each) or not. Store it as an **adjacency list**: a dict from each node to its neighbours, a list for an unweighted graph or a dict of neighbour to weight for a weighted one, adding both directions for an undirected graph. Memory is proportional to nodes plus edges; a matrix of every pair costs nodes squared and suits only dense graphs.
- **Breadth-first search** from a start: a queue, and a dict of hops (or a visited set) that doubles as "seen". Nodes come out in discovery order, so the first time a node is reached is along a **fewest-edges** path; recording each node's **parent** lets you rebuild it. Finds everything **reachable** in `O(V + E)`. The example's fewest-roads route from A to F is A, B, D, F.
- **Depth-first search**, with a stack or recursion, reaches the same nodes in a different order; with a set of the nodes **on the current path**, it detects a **cycle** in a directed graph (an edge back to a node still on the path). Either search needs its visited set: without one, a graph with a loop never ends.
- **Dijkstra's algorithm** finds the **cheapest** path when edges have non-negative weights: tentative distances, and a heap of `(distance, node)` from which the closest unsettled node is popped next and its edges **relaxed** (improved if going through it is shorter); stale heap entries are skipped. `O((V + E) log V)`. The cheapest A to F is 20 km along A, C, E, D, F, against the fewest-roads route's 25.
- **Topological order** of a **DAG** (directed acyclic graph) lists the nodes so that every edge points forward. **Kahn's algorithm**: count each node's incoming edges (**in-degree**), queue the nodes with none, and as each is taken decrement its successors' counts, queueing any that reach zero; nodes left over mean a cycle, and no order exists. The standard library has `graphlib.TopologicalSorter`. The example's pipeline runs load, clean, features, report, train, evaluate; adding an edge from evaluate back to clean makes it unschedulable.
- **The forward pass is a topological order, and backpropagation is its reverse.** A network's computation graph (inputs, weights, multiply, add, subtract, square) is a DAG; running it forward in topological order means every operation's inputs are ready, and walking that order backwards means every node's gradient is complete before it is used. Module 4's layers were a chain, where the order is just the layers in sequence.
- **In machine learning:** autograd engines build and sort exactly this graph; pipeline schedulers run DAGs of steps; nearest-neighbour graphs, knowledge graphs and graph neural networks store data as adjacency lists; and shortest paths, reachability and cycle checks are the questions asked of all of them.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/predict-an-adjacency-list.yaml",
    f'''id: predict-an-adjacency-list
type: predict_output
rev: 1
prompt: |
  Four undirected edges turned into an adjacency list. What does the program print?
code: |
{block(PREDICT_ADJACENCY)}expected_output: |
{block(PREDICT_ADJACENCY_OUT)}explanation: |
  Each edge is added in both directions, in the order the edges come: `c` gains `a` (from the second edge), `b` (third) and `d` (fourth). `a` has two neighbours and `d` one. The number of neighbours is the node's degree.
skills: [represent]
''',
)

write(
    "recall/parsons-hops-by-queue.yaml",
    "id: parsons-hops-by-queue\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to count the hops from `a` to every node by breadth-first search, and print `{'a': 0, 'b': 1, 'c': 1, 'd': 2}`. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("            hops[neighbour] = hops[node]")
    + "\nexplanation: |\n"
    + block("A neighbour discovered from `node` is one hop further than `node`, which is what the `+ 1` records; the decoy copies the distance instead, giving every node 0. The queue hands nodes out in discovery order, so `d`, reached from `b` before `c` gets to it, is correctly 2 hops away.")
    + "skills: [search]\n",
)

mcq(
    "mcq-fewest-edges",
    "You need the route with the fewest changes between two stations on an unweighted metro map. Which search, and why?",
    [
        "Depth-first search, because it follows one line as far as it goes, which is what a traveller does, and it finds a path faster",
        "Breadth-first search: it discovers stations in order of hops, so the goal is first reached along a fewest-edges path",
        "Dijkstra's algorithm, because any shortest-path question needs a heap",
        "A topological sort, which lists stations in order of distance from the start",
    ],
    1,
    "A queue hands out stations in the order they were found, so every station at one hop is seen before any at two hops, and the parent links give the path. Depth-first search finds a path, not the shortest. Dijkstra's algorithm would work with every edge weighted 1, but breadth-first search is the same answer without the heap. A topological sort is for directed acyclic graphs, and a metro map has cycles.",
    ["search"],
)

mcq(
    "mcq-why-the-closest-first",
    "Dijkstra's algorithm always settles the unsettled node with the smallest tentative distance next. Why that one, and what does the heap contribute?",
    [
        "Because nothing can reach it more cheaply: every other unsettled node is at least as far; the heap makes the pick a cheap pop",
        "Because the closest node has the fewest edges, so it is the fastest to process",
        "Because the heap keeps the nodes sorted by distance, so the algorithm can process them in order without comparing anything else",
        "Because settling the farthest node first would require negative weights",
    ],
    0,
    "With non-negative weights, the closest unsettled node's tentative distance is already final: any path to it through another unsettled node is at least as long. That is what makes settling it safe. The heap's job is only to find that node quickly; it isn't sorted, and the algorithm still compares when it relaxes edges. Negative weights break the argument, which is why Dijkstra forbids them.",
    ["dijkstra"],
)

write(
    "recall/predict-a-topological-order.yaml",
    f'''id: predict-a-topological-order
type: predict_output
rev: 1
prompt: |
  Kahn's algorithm on a four-step graph: in-degrees first, then the order. What does the program print?
code: |
{block(PREDICT_TOPO)}expected_output: |
{block(PREDICT_TOPO_OUT)}explanation: |
  `a` has no incoming edges, `b` and `c` have one each (from `a`), `d` has two. Only `a` is ready at first; taking it frees `b` and `c` in that order, and `d` becomes ready only after both of them have been taken, so it comes last. Every edge points forward in the result.
skills: [topo]
''',
)

mcq(
    "mcq-no-order-means",
    "Kahn's algorithm on a pipeline's dependency graph stops with two steps never placed. What does that mean, and what can be done?",
    [
        "The two steps are unreachable from the first step, so they can safely run in any order at the end of the schedule, after everything else",
        "The algorithm needs to be run again with a different starting step",
        "The graph has a cycle through those steps: each waits for the other, so no order exists; a dependency must be removed",
        "The two steps have the same in-degree and the queue cannot choose between them",
    ],
    2,
    "A node is placed when its in-degree reaches zero. Nodes left over have in-degrees that never reached zero, which means each still has an incoming edge from another leftover node: a cycle. Ties in in-degree are fine (the queue takes either), and the start doesn't matter; a cycle is a property of the graph, and only breaking it helps.",
    ["topo"],
)

mcq(
    "mcq-the-backward-pass",
    "A network's computation graph is run forward in topological order. In which order does backpropagation visit the nodes, and why?",
    [
        "The same order, because gradients are computed alongside values",
        "The reverse of the forward order, so every node that uses a value has added its gradient before that value's is used",
        "Breadth-first from the loss, because the loss is the root of the tree and the layers nearest it must always be handled first",
        "Any order, because each node's gradient depends only on its own inputs",
    ],
    1,
    "A node's gradient is the sum of contributions from every node that consumed its output, and those consumers come later in the forward order. Visiting the forward order backwards guarantees all of them have been handled first. Module 4's chain of layers is the simplest case: layers in sequence forward, the sequence reversed backward.",
    ["topo"],
)

write(
    "recall/review-predict-dijkstra-settles.yaml",
    f'''id: review-predict-dijkstra-settles
type: predict_output
rev: 1
prompt: |
  Dijkstra's algorithm on four nodes, printing each node as it is settled. What does the program print?
code: |
{block(REVIEW_DIJKSTRA)}expected_output: |
{block(REVIEW_DIJKSTRA_OUT)}explanation: |
  A is settled at 0 and pushes B at 1 and C at 4. B pops next and pushes C at 3, which beats the direct 4: the heap now holds both entries, pops the 3 first, settles C at 3, and skips the stale 4 when it surfaces. D is reached from C at 4. The closest unsettled node always comes out first.
skills: [dijkstra]
''',
)

mcq(
    "review-mcq-list-or-matrix",
    "A social network has 10 million users and 1 billion friendships. Store it as adjacency lists or as a matrix of every pair?",
    [
        "Adjacency lists: about a billion entries, users plus friendships; a matrix needs 10 million squared cells",
        "A matrix, because checking whether two users are friends should be one lookup",
        "A matrix, because a billion friendships is too many for lists",
        "Neither fits in memory; a graph that size must be stored on disk whatever the representation, and queried in pieces",
    ],
    0,
    "The matrix has a cell for every pair of users, 10 million squared, almost all of them empty. Adjacency lists store only the friendships that exist. Checking friendship in a list is a scan of one user's friends, or one lookup if each user's neighbours are kept in a set. A billion entries fits in memory on a large machine; a hundred million million do not.",
    ["represent"],
)

mcq(
    "review-mcq-looping-forever",
    "A breadth-first search over a road map never finishes. The most likely cause?",
    [
        "The map is too large for a queue; a stack should be used instead, since it holds fewer nodes at a time",
        "The search never marks nodes as seen, so a circuit of roads is walked forever",
        "Breadth-first search only works on trees, and a road map has cycles",
        "The queue was a `deque`, which has no end",
    ],
    1,
    "Roads form circuits, and a search that doesn't remember where it has been keeps rediscovering the same cities and queueing them again. The visited set (or the hops dict) is what makes a search on a graph terminate; the structure of the queue or stack doesn't matter for that. Breadth-first search works fine on graphs with cycles once nodes are marked.",
    ["search"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-a-map-and-a-pipeline/exercise.yaml",
    f'''id: example-a-map-and-a-pipeline
stage: worked_example
rev: 1
title: "A map and a pipeline"
prompt: |
  A road map stored as a dict, searched for the fewest roads and the fewest kilometres; then a pipeline's steps put in an order that respects their dependencies, a cycle caught, and a network's computation graph ordered forward and backward. Press **Run**, then read how each part works.
steps:
  - label: "A map as an adjacency list"
    lines: "{ln('roads = [')}-{ln('neighbours of C:')}"
    note: "Seven roads between six cities, each with a length. The graph is a dict from each city to a dict of its neighbours and the distance to each; every road is added in both directions. C's neighbours are A, B and E."
  - label: "Breadth-first search, with parents"
    lines: "{ln('def breadth_first')}-{ln('    return hops, parent')}"
    note: "A queue of cities to expand and a dict of hops that also records which cities have been seen. Each city taken from the front adds its unseen neighbours to the back, one hop further, and notes itself as their parent. Cities come out in order of hops, so the first discovery of a city is along a fewest-roads path."
  - label: "Rebuilding a path"
    lines: "{ln('def path_to')}-{ln('fewest roads A to F')}"
    note: "Following parent links from F back to A gives the path reversed. The fewest-roads route is A, B, D, F: three roads, which happen to be long ones."
  - label: "Dijkstra's algorithm"
    lines: "{ln('def dijkstra')}-{ln('    return distance, parent')}"
    note: "Tentative distances start at 0 for A. A heap of (distance, city) pops the closest unsettled city; its edges are relaxed, meaning each neighbour's distance is improved if going through this city is shorter, and the improved neighbour is pushed. A city popped a second time is already settled and skipped."
  - label: "Fewest kilometres"
    lines: "{ln('distance, parent = dijkstra')}-{ln('cheapest A to F')}"
    note: "The cheapest route to F is 20 km along A, C, E, D, F, five cities instead of four: more roads, fewer kilometres. The two searches answer two different questions on the same graph."
  - label: "A pipeline in topological order"
    lines: "{ln('pipeline = ')}-{ln('after evaluate')}"
    note: "Six steps with arrows from each to what depends on it. Kahn's algorithm counts incoming arrows, starts with the steps that have none, and releases a step when its last incoming arrow has been taken: load, clean, features, report, train, evaluate. An arrow from evaluate back to clean leaves steps that never become ready, which is what a cycle looks like, and the function says so."
  - label: "The forward pass and the backward pass"
    lines: "{ln('computation = ')}-{ln('backward pass')}"
    note: "The computation graph of `loss = (w * x + b - y) ** 2` as a DAG: inputs feed operations, operations feed the next. Its topological order is the forward pass, with every operation's inputs ready before it runs; the same list reversed is the order backpropagation takes, so every node's gradient is complete before it is used."
''',
)
write("exercises/example-a-map-and-a-pipeline/solution.py", EXAMPLE)
write(
    "exercises/example-a-map-and-a-pipeline/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the neighbours, the hops and fewest-roads path, the distances and cheapest path, the pipeline order and its cycle, and the two passes."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-fewest-hops-path/exercise.yaml",
    f'''id: fill-fewest-hops-path
stage: fill_in
rev: 1
title: "A fewest-hops path"
prompt: |
  `fewest_hops_path(graph, start, goal)` should find a path with the fewest edges by breadth-first search, recording each node's parent when it is first discovered, then walking the parents back from the goal. Replace each `...` so the program prints a path through the metro from A to F, one from E to B, and `None` for the unreachable G:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "A node is new if it has no parent yet: `parent` is the dict that also records what has been seen."
  - "The parent of a newly discovered neighbour is the node it was discovered from."
skills: [search]
''',
)
write("exercises/fill-fewest-hops-path/starter.py", FILL_STARTER)
write("exercises/fill-fewest-hops-path/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-fewest-hops-path/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the three results."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_a_grid():
    """On a 20 by 20 grid, the path from one corner to the opposite one has 39 nodes."""
    fewest_hops_path = function("fewest_hops_path")
    grid = {{}}
    for r in range(20):
        for c in range(20):
            grid[(r, c)] = [(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= r + dr < 20 and 0 <= c + dc < 20]
    path = fewest_hops_path(grid, (0, 0), (19, 19))
    assert len(path) == 39 and path[0] == (0, 0) and path[-1] == (19, 19)
''',
)
write("exercises/fill-fewest-hops-path/wrong/pops-the-back.py", FILL_WRONG)
write(
    "exercises/fill-fewest-hops-path/wrong/typed-in.py",
    "def fewest_hops_path(graph, start, goal):\n    return None\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-has-cycle/exercise.yaml",
    f'''id: write-has-cycle
stage: write
rev: 1
title: "Has a cycle?"
prompt: |
  Write `has_cycle(graph)` for a directed graph given as a dict from each node to the list of nodes it points at: `True` if some path leads back to a node on itself. Use depth-first search with two sets, the nodes on the **current path** (an edge to one of those is a cycle) and the nodes already fully explored (safe to skip). Then print it for these three graphs:

  ```python
  print(has_cycle({{"a": ["b"], "b": ["c"], "c": []}}))
  print(has_cycle({{"a": ["b"], "b": ["c"], "c": ["a"]}}))
  print(has_cycle({{"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}}))
  ```

  ```
{block(WRITE_OUT)}  ```

  The third graph reaches `d` twice without a cycle: a node that was finished is not the same as a node still on the path.
hints:
  - "A recursive `visit(node)`: a node on the path means a cycle; a finished node means no; otherwise add it to the path, visit its neighbours, then move it from the path to the finished set."
  - "Start a visit from every node, so that a cycle not reachable from the first node is still found."
skills: [search]
''',
)
write("exercises/write-has-cycle/starter.py", "")
write("exercises/write-has-cycle/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-has-cycle/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints False, True, False."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_more_graphs():
    """A self-loop is a cycle; a chain of 300 nodes is not; a cycle away from the first node is still found."""
    has_cycle = function("has_cycle")
    assert has_cycle({{"a": ["a"]}})
    chain = {{i: [i + 1] for i in range(299)}}
    chain[299] = []
    assert not has_cycle(chain)
    assert has_cycle({{"a": [], "b": ["c"], "c": ["b"]}})
''',
)
write("exercises/write-has-cycle/wrong/finished-counts-as-cycle.py", WRITE_WRONG)
write(
    "exercises/write-has-cycle/wrong/typed-in.py",
    "def has_cycle(graph):\n    return False\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-a-graph-toolkit/exercise.yaml",
    f'''id: build-a-graph-toolkit
stage: build
rev: 1
title: "A graph toolkit"
prompt: |
  Starting from a blank editor, write four functions over graphs stored as dicts:

  - `shortest_hops(graph, start)`: a dict from every reachable node to its hops from `start`, by breadth-first search (the graph maps each node to a list, or a dict, of neighbours).
  - `cheapest_path(graph, start, goal)`: for a weighted graph (each node maps to a dict of neighbour to cost), the tuple `(cost, path)` of a cheapest path from `start` to `goal` by Dijkstra's algorithm with a heap, or `None` if the goal is unreachable.
  - `topological_order(graph)`: for a directed graph (each node maps to the list it points at), a list in which every edge points forward, by Kahn's algorithm; raise `ValueError` if the graph has a cycle. Take ready nodes in the order they become ready, starting from the dict's order.
  - `has_cycle(graph)`: whether a directed graph has a cycle.

  Then print:

  ```python
  roads = {{"A": {{"B": 4, "C": 2}}, "B": {{"A": 4, "C": 5, "D": 10}}, "C": {{"A": 2, "B": 5, "E": 3}}, "D": {{"B": 10, "E": 4, "F": 11}}, "E": {{"C": 3, "D": 4}}, "F": {{"D": 11}}}}
  print(shortest_hops(roads, "A"))
  print(cheapest_path(roads, "A", "F"))
  pipeline = {{"load": ["clean"], "clean": ["features", "report"], "features": ["train"], "train": ["evaluate"], "report": [], "evaluate": []}}
  print(topological_order(pipeline), has_cycle(pipeline))
  print(has_cycle({{"a": ["b"], "b": ["a"]}}))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks use a 40 by 40 grid, a map where the direct road is dearer than a detour, a chain of 400 steps, and graphs with and without cycles.
skills: [search, dijkstra, topo]
''',
)
write("exercises/build-a-graph-toolkit/starter.py", "")
write("exercises/build-a-graph-toolkit/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-a-graph-toolkit/test_exercise.py",
    f'''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def grid(size):
    cells = {{}}
    for r in range(size):
        for c in range(size):
            cells[(r, c)] = [(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= r + dr < size and 0 <= c + dc < size]
    return cells


def test_the_output():
    """Prints the four lines."""
    assert run() == {BUILD_OUT!r}


def test_hops_on_a_grid():
    """On a 40 by 40 grid, the opposite corner is 78 hops away and every cell is reached."""
    shortest_hops = function("shortest_hops")
    hops = shortest_hops(grid(40), (0, 0))
    assert len(hops) == 1600 and hops[(39, 39)] == 78 and hops[(0, 39)] == 39


def test_cheapest_takes_the_detour():
    """A direct road of 10 loses to a detour of 2 + 3 + 4, and an unreachable goal gives None."""
    cheapest_path = function("cheapest_path")
    roads = {{"S": {{"T": 10, "A": 2}}, "A": {{"B": 3}}, "B": {{"T": 4}}, "T": {{}}, "X": {{}}}}
    assert cheapest_path(roads, "S", "T") == (9, ["S", "A", "B", "T"])
    assert cheapest_path(roads, "S", "X") is None


def test_topological_order():
    """A chain of 400 steps comes out in chain order, a diamond respects its edges, and a cycle raises ValueError."""
    topological_order = function("topological_order")
    chain = {{i: [i + 1] for i in range(399)}}
    chain[399] = []
    assert topological_order(chain) == list(range(400))
    order = topological_order({{"d": [], "a": ["b", "c"], "b": ["d"], "c": ["d"]}})
    assert order.index("a") < order.index("b") < order.index("d") and order.index("a") < order.index("c") < order.index("d")
    try:
        topological_order({{"a": ["b"], "b": ["c"], "c": ["a"]}})
    except ValueError:
        pass
    else:
        raise AssertionError("a cycle should raise ValueError")


def test_has_cycle():
    """A self-loop and a two-node loop are cycles; a chain and a diamond are not."""
    has_cycle = function("has_cycle")
    assert has_cycle({{"a": ["a"]}}) and has_cycle({{"x": [], "a": ["b"], "b": ["a"]}})
    assert not has_cycle({{"a": ["b"], "b": ["c"], "c": []}}) and not has_cycle({{"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}})
''',
)
write("exercises/build-a-graph-toolkit/wrong/hops-by-stack.py", BUILD_DFS_HOPS)
write("exercises/build-a-graph-toolkit/wrong/first-path-wins.py", BUILD_GREEDY_PATH)
write("exercises/build-a-graph-toolkit/wrong/no-cycle-check.py", BUILD_TOPO_NO_CYCLE_CHECK)
write(
    "exercises/build-a-graph-toolkit/wrong/typed-in.py",
    "def shortest_hops(graph, start):\n    return {}\n\n\ndef cheapest_path(graph, start, goal):\n    return None\n\n\ndef topological_order(graph):\n    return list(graph)\n\n\ndef has_cycle(graph):\n    return False\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-scheduler/exercise.yaml",
    f'''id: debug-a-scheduler
stage: debug
rev: 1
title: "A scheduler that gets stuck"
prompt: |
  `schedule(graph)` should list a pipeline's steps in an order that respects every arrow (Kahn's algorithm) and say whether every step was placed. The program should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the schedule starts with `report` and `evaluate`, the steps that nothing depends on, and then gets stuck, because the counting loop adds to the **source** of each arrow instead of its target: it counts outgoing arrows, not incoming ones. Fix that, and the schedule is `['load']` and stuck: when a step is taken, each step it points at must have its incoming count reduced, or nothing ever becomes ready. The cyclic graph should stay stuck either way.
skills: [topo]
''',
)
write("exercises/debug-a-scheduler/starter.py", DEBUG_STARTER)
write("exercises/debug-a-scheduler/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-scheduler/test_exercise.py",
    f'''from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the complete schedule and the stuck cycle."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_other_graphs():
    """A diamond is placed completely with its edges forward; a self-loop is stuck."""
    schedule = function("schedule")
    order, complete = schedule({{"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}})
    assert complete and order.index("a") < order.index("b") < order.index("d") and order.index("c") < order.index("d")
    assert schedule({{"a": ["a"]}}) == ([], False)
''',
)
write("exercises/debug-a-scheduler/wrong/still-counts-outgoing.py", DEBUG_STILL_OUTDEGREE)
write("exercises/debug-a-scheduler/wrong/still-never-releases.py", DEBUG_STILL_NO_DECREMENT)
write(
    "exercises/debug-a-scheduler/wrong/typed-in.py",
    "def schedule(graph):\n    return list(graph), True\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-reachable/exercise.yaml",
    f'''id: review-reachable
stage: review_code
rev: 1
title: "Reachable, from memory"
prompt: |
  Write `reachable(graph, start)`, the set of every node that can be reached from `start` (including `start`) in a directed graph given as a dict of lists, by breadth-first or depth-first search with a visited set. Print the sorted sets for `a`, `d` and `c` in `{{"a": ["b"], "b": ["c", "a"], "c": [], "d": ["a"]}}`:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [search]
''',
)
write("exercises/review-reachable/starter.py", "")
write("exercises/review-reachable/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-reachable/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the three sorted sets."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_a_cycle_terminates():
    """A graph that is one big cycle is fully reachable from any node, and the search ends."""
    reachable = function("reachable")
    ring = {{i: [(i + 1) % 500] for i in range(500)}}
    assert reachable(ring, 0) == set(range(500))
''',
)
write(
    "exercises/review-reachable/wrong/no-visited-set.py",
    REVIEW_CODE_SOLUTION.replace("    seen = {start}\n    queue = deque([start])\n    while queue:\n        node = queue.popleft()\n        for neighbour in graph[node]:\n            if neighbour not in seen:\n                seen.add(neighbour)\n                queue.append(neighbour)\n    return seen", "    seen = {start}\n    for neighbour in graph[start]:\n        seen.add(neighbour)\n    return seen"),
)
write(
    "exercises/review-reachable/wrong/typed-in.py",
    "def reachable(graph, start):\n    return {start}\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.dsa.graphs written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
