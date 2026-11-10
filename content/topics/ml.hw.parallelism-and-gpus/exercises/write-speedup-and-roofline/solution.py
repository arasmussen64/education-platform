def speedup(parallel_fraction, workers):
    """Amdahl's law: the serial part is untouched, the parallel part is divided by the workers."""
    return 1 / ((1 - parallel_fraction) + parallel_fraction / workers)


def roofline_seconds(flops, bytes_moved, flop_rate, bandwidth):
    """The time a machine needs for the arithmetic or for the bytes, whichever is longer: it overlaps the two."""
    return max(flops / flop_rate, bytes_moved / bandwidth)


print(round(speedup(0.9, 8), 2), round(speedup(0.9, 10**6), 2))
print(round(roofline_seconds(2 * 1024**3, 3 * 1024**2 * 4, 10e12, 500e9) * 1e6, 1))
print(round(roofline_seconds(1_000_000, 12_000_000, 10e12, 500e9) * 1e6, 1))
