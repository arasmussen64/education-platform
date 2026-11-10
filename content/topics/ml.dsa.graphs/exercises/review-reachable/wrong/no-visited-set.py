from collections import deque


def reachable(graph, start):
    """Every node that can be reached from start, including start, as a set."""
    seen = {start}
    for neighbour in graph[start]:
        seen.add(neighbour)
    return seen


graph = {"a": ["b"], "b": ["c", "a"], "c": [], "d": ["a"]}
print(sorted(reachable(graph, "a")), sorted(reachable(graph, "d")), sorted(reachable(graph, "c")))
