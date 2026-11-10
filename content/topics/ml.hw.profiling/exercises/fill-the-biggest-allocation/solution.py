import tracemalloc


def biggest_allocation(function):
    """Run the function under tracemalloc and return the line number and the bytes of the line that allocated the most."""
    tracemalloc.start()
    kept = function()
    snapshot = tracemalloc.take_snapshot()
    tracemalloc.stop()
    top = snapshot.statistics("lineno")[0]
    return top.traceback[0].lineno, top.size


def build():
    small = [float(i) for i in range(100)]
    big = [float(i) for i in range(100_000)]
    return small, big


line, size = biggest_allocation(build)
print(line == build.__code__.co_firstlineno + 2, size > 100_000 * 8)
