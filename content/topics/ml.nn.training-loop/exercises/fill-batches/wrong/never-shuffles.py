import numpy as np


def batches(n, batch_size, rng):
    """Index arrays covering 0..n-1 once, in a fresh random order, batch_size at a time; the last batch may be short."""
    order = np.arange(n)
    for start in range(0, n, batch_size):
        yield order[start : start + batch_size]


rng = np.random.default_rng(0)
epoch_one = list(batches(10, 4, rng))
epoch_two = list(batches(10, 4, rng))
print([len(index) for index in epoch_one], sorted(np.concatenate(epoch_one).tolist()))
print(bool((np.concatenate(epoch_one) == np.concatenate(epoch_two)).all()))
