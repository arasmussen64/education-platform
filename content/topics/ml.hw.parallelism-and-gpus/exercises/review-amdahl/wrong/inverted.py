def speedup(parallel_fraction, workers):
    """Amdahl's law."""
    return 1 / (parallel_fraction + (1 - parallel_fraction) / workers)


print(round(speedup(0.8, 4), 2), round(speedup(0.8, 64), 2), round(speedup(0.8, 10**9), 2))
