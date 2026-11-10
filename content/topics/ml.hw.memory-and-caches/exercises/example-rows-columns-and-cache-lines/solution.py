from collections import OrderedDict

import numpy as np

a = np.arange(12, dtype=np.float64).reshape(3, 4)
print("strides:", a.strides, "| transposed:", a.T.strides, "| contiguous:", a.flags["C_CONTIGUOUS"], a.T.flags["C_CONTIGUOUS"])
print("a[1, 2] sits", 1 * a.strides[0] + 2 * a.strides[1], "bytes from the start; row 1 occupies bytes", a.strides[0], "to", 2 * a.strides[0] - 1)

every_other_column = a[:, ::2]
big_ones = a[a > 5]
print("shares memory: slice", np.shares_memory(a, every_other_column), "| mask", np.shares_memory(a, big_ones), "| slice strides", every_other_column.strides)
every_other_column[0, 0] = 100
print("after writing 100 through the view, a[0, 0] is", a[0, 0])


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


for order in ("rows", "columns"):
    print(f"256 x 256 floats walked by {order}, 64 lines of cache: {misses((256, 256), order, 64):,} misses")

grid = np.zeros((1000, 1000), dtype=np.float64)
print("a 1000 x 1000 float64 grid is", f"{grid.nbytes:,}", "bytes")
doubled = grid + 1
grid += 1
print("grid + 1 made a new block:", not np.shares_memory(grid, doubled), "| grid += 1 wrote in place:", grid[0, 0])
