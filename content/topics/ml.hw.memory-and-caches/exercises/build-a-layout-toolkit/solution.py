from collections import OrderedDict

import numpy as np


def c_strides(shape, itemsize):
    """The byte strides of a C-order array of that shape and item size."""
    strides = []
    step = itemsize
    for size in reversed(shape):
        strides.append(step)
        step *= size
    return tuple(reversed(strides))


def byte_offset(shape, itemsize, index):
    """How many bytes from the start of a C-order array the element at index sits."""
    return sum(i * s for i, s in zip(index, c_strides(shape, itemsize)))


def misses(shape, order, lines_in_cache, floats_per_line=8):
    """Cache misses when a float64 matrix is walked in row or column order through a small least-recently-used cache."""
    rows, cols = shape
    if order == "rows":
        visits = ((r, c) for r in range(rows) for c in range(cols))
    else:
        visits = ((r, c) for c in range(cols) for r in range(rows))
    cache = OrderedDict()
    count = 0
    for r, c in visits:
        line = (r, c // floats_per_line)
        if line in cache:
            cache.move_to_end(line)
        else:
            count += 1
            cache[line] = True
            if len(cache) > lines_in_cache:
                cache.popitem(last=False)
    return count


def traffic(shape, dtype, reads, writes):
    """Bytes moved by an operation that reads the whole array `reads` times and writes it `writes` times."""
    elements = 1
    for size in shape:
        elements *= size
    return elements * np.dtype(dtype).itemsize * (reads + writes)


print(c_strides((3, 4), 8), byte_offset((3, 4), 8, (1, 2)), byte_offset((2, 3, 4), 2, (1, 2, 3)))
print(misses((256, 256), "rows", 64), misses((256, 256), "columns", 64))
print(traffic((1000, 1000), "float64", 1, 0), traffic((1000, 1000), "float64", 1, 1), traffic((1000, 1000), "float32", 1, 1))
