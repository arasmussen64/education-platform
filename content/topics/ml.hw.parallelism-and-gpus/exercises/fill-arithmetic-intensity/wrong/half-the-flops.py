def arithmetic_intensity(m, k, n, itemsize):
    """FLOPs per byte of (m, k) @ (k, n): two operations per term of each output, over the bytes of both inputs and the output."""
    flops = m * k * n
    bytes_moved = (m * k + k * n + m * n) * itemsize
    return flops / bytes_moved


print(round(arithmetic_intensity(1024, 1024, 1024, 4), 1))
print(round(arithmetic_intensity(1, 1024, 1024, 4), 1), round(arithmetic_intensity(64, 1024, 1024, 4), 1))
