import numpy as np


def batches(n, batch_size, rng):
    """Index arrays covering 0..n-1 once in a fresh random order, batch_size at a time; the last may be short."""
    order = np.arange(n)
    for start in range(0, n, batch_size):
        yield order[start : start + batch_size]


rng = np.random.default_rng(3)
first = list(batches(23, 5, rng))
second = list(batches(23, 5, rng))
print([len(index) for index in first], sorted(np.concatenate(first).tolist()) == list(range(23)))
print(bool((np.concatenate(first) == np.concatenate(second)).all()))
