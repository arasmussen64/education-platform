import heapq
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
