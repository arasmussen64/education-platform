import math


def softmax(logits):
    """exp(logits) scaled to sum to 1, with the largest logit pulled out so nothing overflows."""
    biggest = max(logits)
    weights = [math.exp(x - biggest) for x in logits]
    total = sum(weights)
    return [w / total for w in weights]


def cross_entropy(logits, true_index):
    """Minus the log of the probability given to the true class."""
    return -math.log(softmax(logits)[true_index])


batch = [([2.0, 1.0, 0.1], 0), ([1000.0, 1001.0, 999.0], 1), ([0.0, 0.0, 0.0], 2)]
losses = [cross_entropy(logits, true_index) for logits, true_index in batch]
print("losses:", [round(loss, 4) for loss in losses], "mean:", round(sum(losses) / len(losses), 4))
print("probabilities sum to 1:", all(math.isclose(sum(softmax(logits)), 1.0) for logits, _ in batch))
