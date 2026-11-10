import numpy as np


def byte_offset(shape, itemsize, index):
    """Bytes from the start of a C-order array to the element at index: each earlier axis steps a whole block of later axes."""
    row, col = index
    rows, cols = shape
    return (row * cols + col) * itemsize


def clear_top_row(a):
    """Set the first row of a 2-D array to zero, in place."""
    top = a[0].copy()
    top[:] = 0


a = np.arange(12, dtype=np.float64).reshape(3, 4)
print(byte_offset(a.shape, a.itemsize, (1, 2)), "==", 1 * a.strides[0] + 2 * a.strides[1])
clear_top_row(a)
print(a[0], a[1, 0])
