from collections import deque


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
            if indegree[next_node] == 0:
                ready.append(next_node)
    return order, len(order) == len(graph)


pipeline = {"load": ["clean"], "clean": ["features", "report"], "features": ["train"], "train": ["evaluate"], "report": [], "evaluate": []}
order, complete = schedule(pipeline)
print(order, "complete" if complete else "stuck")
print(schedule({"a": ["b"], "b": ["c"], "c": ["a"]}))
