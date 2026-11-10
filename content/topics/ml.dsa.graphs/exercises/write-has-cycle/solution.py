def has_cycle(graph):
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
