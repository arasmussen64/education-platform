import heapq
import random
from collections import deque


class Node:
    def __init__(self, value, children=()):
        self.value = value
        self.children = list(children)


tree = Node("root", [Node("a", [Node("a1"), Node("a2")]), Node("b"), Node("c", [Node("c1", [Node("c1x")])])])


def depth_first(node):
    """Visit the node, then each child's whole subtree: recursion."""
    order = [node.value]
    for child in node.children:
        order.extend(depth_first(child))
    return order


def breadth_first(node):
    """Visit level by level: a queue."""
    order = []
    queue = deque([node])
    while queue:
        current = queue.popleft()
        order.append(current.value)
        queue.extend(current.children)
    return order


def depth(node):
    return 1 + max((depth(child) for child in node.children), default=0)


print("depth-first:", depth_first(tree))
print("breadth-first:", breadth_first(tree))
print("depth:", depth(tree))


class BSTNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def bst_insert(root, value):
    """Walk down: smaller goes left, larger goes right; hang the new node where the walk falls off."""
    if root is None:
        return BSTNode(value)
    node = root
    while True:
        side = "left" if value < node.value else "right"
        if getattr(node, side) is None:
            setattr(node, side, BSTNode(value))
            return root
        node = getattr(node, side)


def bst_search(root, value, counter):
    node = root
    while node is not None:
        counter[0] += 1
        if value == node.value:
            return True
        node = node.left if value < node.value else node.right
    return False


values = list(range(1000))
random.Random(2).shuffle(values)
shuffled_root = None
for value in values:
    shuffled_root = bst_insert(shuffled_root, value)
sorted_root = None
for value in range(1000):
    sorted_root = bst_insert(sorted_root, value)
for name, root in (("shuffled", shuffled_root), ("sorted", sorted_root)):
    counter = [0]
    assert bst_search(root, 999, counter)
    print(name, "insert order: finding 999 took", counter[0], "comparisons")

rng = random.Random(3)
stream = [rng.randint(1, 1_000_000) for _ in range(10_000)]
heap = []
for value in stream:
    heapq.heappush(heap, value)
    if len(heap) > 5:
        heapq.heappop(heap)
print("top 5 of 10,000:", sorted(heap, reverse=True))
print("the heap list itself:", heap, "(smallest first; the rest is not sorted)")
print("heapq.nlargest agrees:", heapq.nlargest(5, stream) == sorted(heap, reverse=True))

decision_tree = ("petal_length", 2.5, ("petal_width", 1.7, "virginica", "versicolor"), "setosa")


def decide(tree, flower):
    """Walk from the root question to a leaf: a tuple asks a question, a string is the answer."""
    steps = 0
    while isinstance(tree, tuple):
        feature, threshold, if_greater, if_not = tree
        tree = if_greater if flower[feature] > threshold else if_not
        steps += 1
    return tree, steps


for flower in ({"petal_length": 1.4, "petal_width": 0.2}, {"petal_length": 4.7, "petal_width": 1.4}, {"petal_length": 5.9, "petal_width": 2.1}):
    print(flower, "->", decide(decision_tree, flower))
