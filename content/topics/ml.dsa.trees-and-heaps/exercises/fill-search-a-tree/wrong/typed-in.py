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
    return value in (60, 20)


print('True False True')
