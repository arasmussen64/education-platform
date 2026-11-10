import math


def softmax(xs):
    """exp(xs) scaled to sum to 1, computed so that large inputs don't overflow."""
    weights = [math.exp(x) for x in xs]
    total = sum(weights)
    return [w / total for w in weights]


print([round(p, 4) for p in softmax([1.0, 2.0, 3.0])])
print([round(p, 4) for p in softmax([1000.0, 1001.0, 1002.0])])
