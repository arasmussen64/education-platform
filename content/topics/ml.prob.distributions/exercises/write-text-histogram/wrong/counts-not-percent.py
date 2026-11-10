import numpy as np

rng = np.random.default_rng(3)


def histogram(sample, bins):
    counts, edges = np.histogram(sample, bins=bins)
    for count, left, right in zip(counts, edges[:-1], edges[1:]):
        print(f"{left:6.1f} to {right:6.1f} {'#' * round(count / 100)}")


histogram(rng.normal(0, 1, size=10000), bins=np.arange(-4, 5, 1.0))
