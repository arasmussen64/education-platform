def leaves(node):
    """How many nodes have no children: a leaf counts 1, any other node counts its children's leaves."""
    if not node["children"]:
        return 1
    return sum(leaves(child) for child in node["children"])


leaf = lambda value: {"value": value, "children": []}
tree = {"value": "root", "children": [{"value": "a", "children": [leaf("a1"), leaf("a2")]}, leaf("b"), {"value": "c", "children": [leaf("c1")]}]}
print(leaves(tree), leaves(leaf("only")))
