from collections import OrderedDict


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
    print(order, misses((128, 128), order, 32))
print(misses((8, 8), "columns", 8))
