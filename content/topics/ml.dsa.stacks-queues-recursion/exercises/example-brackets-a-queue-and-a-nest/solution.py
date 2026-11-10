from collections import deque


def balanced(text):
    """Are the brackets matched and properly nested? A stack of the openers still waiting."""
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack


for text in ("([]{})", "([)]", "((", "f(x[0]) + g({})"):
    print(repr(text), balanced(text))


class ArrayQueue:
    """A queue on a plain list, with the shifting that pop(0) hides written out."""

    def __init__(self):
        self.items = []
        self.moves = 0

    def push(self, item):
        self.items.append(item)

    def pop_front(self):
        first = self.items[0]
        for i in range(1, len(self.items)):
            self.items[i - 1] = self.items[i]
            self.moves += 1
        self.items.pop()
        return first


slow = ArrayQueue()
fast = deque()
for i in range(2000):
    slow.push(i)
    fast.append(i)
steps = 0
while fast:
    slow.pop_front()
    fast.popleft()
    steps += 1
print("2000 pops: the list moved", slow.moves, "elements; the deque took", steps, "steps")


def countdown(n, depth=0):
    print("  " * depth + "start", n)
    if n > 0:
        countdown(n - 1, depth + 1)
    print("  " * depth + "end", n)


countdown(2)


def flatten(nested):
    """Every number in a nest of lists, in order, by recursion."""
    flat = []
    for item in nested:
        if isinstance(item, list):
            flat.extend(flatten(item))
        else:
            flat.append(item)
    return flat


def flatten_with_a_stack(nested):
    """The same, with a stack you manage instead of the call stack."""
    flat = []
    stack = list(reversed(nested))
    while stack:
        item = stack.pop()
        if isinstance(item, list):
            stack.extend(reversed(item))
        else:
            flat.append(item)
    return flat


data = [1, [2, [3, 4]], [], [[5]], 6]
print(flatten(data), flatten_with_a_stack(data))

deep = [0]
for i in range(1, 5000):
    deep = [i, deep]
print("5000 levels with a stack:", len(flatten_with_a_stack(deep)), "numbers")
try:
    flatten(deep)
    print("5000 levels by recursion: it worked")
except RecursionError:
    print("5000 levels by recursion: RecursionError")
