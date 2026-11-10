class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def insert(root, value):
    if root is None:
        return Node(value)
    node = root
    while True:
        side = "left" if value < node.value else "right"
        if getattr(node, side) is None:
            setattr(node, side, Node(value))
            return root
        node = getattr(node, side)


def contains(root, value):
    """Walk down from the root: left if the value is smaller, right if it is larger."""
    node = root
    while node is not None:
        if value == node.value:
            return True
        node = node.right if value < node.value else node.left
    return False


root = None
for value in (50, 30, 70, 20, 40, 60, 80):
    root = insert(root, value)
print(contains(root, 60), contains(root, 65), contains(root, 20))
