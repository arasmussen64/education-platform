def evaluate_postfix(expression):
    """Evaluate tokens in postfix order: operands push, an operator pops two and pushes the result."""
    stack = []
    for token in expression.split():
        if token in {"+", "-", "*"}:
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b if token == "+" else a - b if token == "-" else a * b)
        else:
            stack.append(int(token))
    return stack.pop()


def balanced(text):
    """Are the brackets matched and properly nested?"""
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack


def max_depth(nested):
    """How deeply lists nest: a non-list is 0, an empty list 1, a list is 1 more than its deepest item."""
    if not isinstance(nested, list):
        return 0
    return 1 + max((max_depth(item) for item in nested), default=0)


def flatten_iterative(nested):
    """Every non-list value, in order, with an explicit stack so that any depth works."""
    flat = []
    stack = list(reversed(nested))
    while stack:
        item = stack.pop()
        if isinstance(item, list):
            stack.extend(reversed(item))
        else:
            flat.append(item)
    return flat


print(evaluate_postfix("3 4 + 2 *"), evaluate_postfix("5 1 2 + 4 * + 3 -"))
print(balanced("([]{})"), balanced("([)]"), balanced(""))
print(max_depth(7), max_depth([]), max_depth([1, [2, [3]]]))
print(flatten_iterative([1, [2, [3, 4]], [], [[5]], 6]))
