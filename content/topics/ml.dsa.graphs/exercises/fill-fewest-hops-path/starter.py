from collections import deque


def fewest_hops_path(graph, start, goal):
    """A path from start to goal with the fewest edges, by breadth-first search with parent links."""
    parent = {start: None}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == goal:
            break
        for neighbour in graph[node]:
            if neighbour not in ...:
                parent[neighbour] = ...
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
