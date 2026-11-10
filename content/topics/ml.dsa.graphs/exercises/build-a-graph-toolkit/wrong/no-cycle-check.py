import heapq
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
