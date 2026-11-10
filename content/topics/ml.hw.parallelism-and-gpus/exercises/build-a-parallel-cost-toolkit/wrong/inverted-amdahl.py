def amdahl(parallel_fraction, workers):
    """The speed-up Amdahl's law allows: the serial part keeps its time, the parallel part is shared."""
    return 1 / (parallel_fraction + (1 - parallel_fraction) / workers)


def matmul_cost(m, k, n, itemsize):
    """(FLOPs, bytes) of (m, k) @ (k, n): a multiply and an add per term, both inputs read and the output written once."""
    return 2 * m * k * n, (m * k + k * n + m * n) * itemsize


def intensity(flops, bytes_moved):
    """FLOPs per byte."""
    return flops / bytes_moved


def roofline_seconds(flops, bytes_moved, flop_rate, bandwidth):
    """The longer of the arithmetic time and the memory time, since the machine overlaps them."""
    return max(flops / flop_rate, bytes_moved / bandwidth)


def transfer_seconds(total_bytes, pieces, bandwidth, latency):
    """Moving total_bytes across a bus in that many pieces: the bytes at the bandwidth, plus a fixed latency per piece."""
    return total_bytes / bandwidth + pieces * latency


print(round(amdahl(0.9, 8), 2), round(amdahl(0.9, 10**9), 2), round(amdahl(0.99, 64), 1))
print(matmul_cost(1024, 1024, 1024, 4), round(intensity(*matmul_cost(1024, 1024, 1024, 4)), 1))
print(round(intensity(*matmul_cost(1, 1024, 1024, 4)), 2), round(intensity(*matmul_cost(512, 1024, 1024, 4)), 1))
print(round(roofline_seconds(*matmul_cost(1024, 1024, 1024, 4), 10e12, 500e9) * 1e6, 1), round(roofline_seconds(1_000_000, 12_000_000, 10e12, 500e9) * 1e6, 1))
print(round(transfer_seconds(10**9, 1, 25e9, 10e-6), 3), round(transfer_seconds(10**9, 10**6, 25e9, 10e-6), 2))
