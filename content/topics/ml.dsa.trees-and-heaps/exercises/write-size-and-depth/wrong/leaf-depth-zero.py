def size(node):
    """How many nodes a tree has: this one plus every child's subtree."""
    return 1 + sum(size(child) for child in node["children"])


def depth(node):
    """How many levels: 1 for a leaf, 1 more than the deepest child otherwise."""
    return max((1 + depth(child) for child in node["children"]), default=0)


leaf = lambda value: {"value": value, "children": []}
tree = {"value": "root", "children": [{"value": "a", "children": [leaf("a1"), leaf("a2")]}, leaf("b"), {"value": "c", "children": [{"value": "c1", "children": [leaf("c1x")]}]}]}
print(size(tree), depth(tree))
print(size(leaf("only")), depth(leaf("only")))
