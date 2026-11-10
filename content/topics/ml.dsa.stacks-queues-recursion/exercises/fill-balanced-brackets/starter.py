def balanced(text):
    """Are the brackets matched and properly nested?"""
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(...)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[...]:
                return False
    return not stack


for text in ("([]{})", "([)]", "((", "f(x[0]) + g({})"):
    print(repr(text), balanced(text))
