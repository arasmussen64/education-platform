import math


def speedup(parallel_fraction, workers):
    """Amdahl's law: the serial part keeps its whole time; only the parallel part is shared out."""
    serial = 1 - parallel_fraction
    return 1 / (serial + parallel_fraction / workers)


for p in (0.5, 0.9, 0.99):
    print(f"{p:.0%} parallel:", " ".join(f"{workers} workers {speedup(p, workers):.1f}x" for workers in (2, 8, 64, 1000)), f"| limit {1 / (1 - p):.0f}x")

items = 1_000_000
print(f"{items:,} independent items on 8 workers: {math.ceil(items / 8):,} steps each | a chain of {items:,} dependent steps on 8 workers: {items:,} steps")


def matmul_cost(m, k, n, itemsize=4):
    """FLOPs and bytes of (m, k) @ (k, n): a multiply and an add for each of the k terms of each of the m * n outputs; read both inputs, write the output."""
    flops = 2 * m * k * n
    bytes_moved = (m * k + k * n + m * n) * itemsize
    return flops, bytes_moved


flops, bytes_moved = matmul_cost(1024, 1024, 1024)
print(f"1024 x 1024 @ 1024 x 1024 in float32: {flops:,} FLOPs, {bytes_moved:,} bytes, {flops / bytes_moved:.0f} FLOPs per byte")
add_flops, add_bytes = 1_000_000, 3 * 1_000_000 * 4
print(f"adding two vectors of a million float32: {add_flops:,} FLOPs, {add_bytes:,} bytes, {add_flops / add_bytes:.2f} FLOPs per byte")

FLOP_RATE, BANDWIDTH = 10e12, 500e9
print(f"a GPU of round numbers, 10 TFLOP/s and 500 GB/s, does {FLOP_RATE / BANDWIDTH:.0f} FLOPs per byte it fetches: above that compute-bound, below it memory-bound")
for name, (f, b) in (("the matrix multiply", (flops, bytes_moved)), ("the vector add", (add_flops, add_bytes))):
    compute, memory = f / FLOP_RATE, b / BANDWIDTH
    print(f"{name}: {compute * 1e6:.1f} us of arithmetic, {memory * 1e6:.1f} us of memory traffic, so it is {'compute' if compute > memory else 'memory'}-bound")

k, n = 1024, 1024
print("FLOPs per byte of (batch, 1024) @ (1024, 1024), the weights read once per batch:", " ".join(f"batch {b}: {matmul_cost(b, k, n)[0] / matmul_cost(b, k, n)[1]:.1f}" for b in (1, 8, 64, 512)))

BUS, LATENCY = 25e9, 10e-6
dataset = 1_000_000_000
print(f"moving a 1 GB dataset to the GPU once: {dataset / BUS * 1000:.0f} ms | as a million 1 KB pieces: {dataset / BUS + 1_000_000 * LATENCY:.0f} s, almost all of it the fixed cost per transfer")
