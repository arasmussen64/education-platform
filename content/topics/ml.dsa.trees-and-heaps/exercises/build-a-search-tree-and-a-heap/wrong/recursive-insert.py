import heapq


class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def bst_insert(root, value):
    """Insert into a binary search tree by walking down, not by recursion; returns the root."""
    if root is None:
        return Node(value)
    if value < root.value:
        root.left = bst_insert(root.left, value)
    else:
        root.right = bst_insert(root.right, value)
    return root


def bst_contains(root, value):
    """Walk down comparing: left if smaller, right if larger."""
    node = root
    while node is not None:
        if value == node.value:
            return True
        node = node.left if value < node.value else node.right
    return False


def top_k(values, k):
    """The k largest values, largest first, keeping a heap of only k values."""
    heap = []
    for value in values:
        heapq.heappush(heap, value)
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted(heap, reverse=True)


def decide(tree, record):
    """A decision tree as nested tuples (feature, threshold, if_greater, if_not); a string is a leaf."""
    while isinstance(tree, tuple):
        feature, threshold, if_greater, if_not = tree
        tree = if_greater if record[feature] > threshold else if_not
    return tree


root = None
for value in (50, 30, 70, 20, 40, 60, 80):
    root = bst_insert(root, value)
print(bst_contains(root, 60), bst_contains(root, 65))
print(top_k([5, 1, 8, 3, 9, 2, 8], 3))
tree = ("petal_length", 2.5, ("petal_width", 1.7, "virginica", "versicolor"), "setosa")
print(decide(tree, {"petal_length": 4.7, "petal_width": 1.4}), decide(tree, {"petal_length": 1.0, "petal_width": 0.1}))
