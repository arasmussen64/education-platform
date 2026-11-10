def amdahl(parallel_fraction, workers):
    """The speed-up from sharing the parallel part among the workers; the serial part keeps its whole time."""
    serial = 1 - parallel_fraction
    return 1 / (parallel_fraction + serial / workers)


def matmul_cost(m, k, n, itemsize):
    """(FLOPs, bytes) of (m, k) @ (k, n): each of the m * n outputs sums k products, a multiply and an add each."""
    flops = m * k * n
    bytes_moved = (m * k + k * n + m * n) * itemsize
    return flops, bytes_moved


print(f"8 workers on 90% parallel work: {amdahl(0.9, 8):.2f}x")
flops, bytes_moved = matmul_cost(1024, 1024, 1024, 4)
print(f"1024-cube matmul: {flops:,} FLOPs, {bytes_moved:,} bytes, {flops / bytes_moved:.1f} FLOPs per byte")
