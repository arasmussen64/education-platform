import cProfile
import pstats
import tracemalloc

import numpy as np


def distance_squared(a, b):
    dx, dy = a[0] - b[0], a[1] - b[1]
    return dx * dx + dy * dy


def nearest(points, queries):
    """For each query, the index of the nearest point: every pair costs a call to distance_squared."""
    result = []
    for q in queries:
        best, best_d = -1, float("inf")
        for i, p in enumerate(points):
            d = distance_squared(p, q)
            if d < best_d:
                best, best_d = i, d
        result.append(best)
    return result


def make_points(n):
    return [((i * 7919) % 1000 / 1000, (i * 104729) % 1000 / 1000) for i in range(n)]


def profile(function, *args):
    """Run the function under cProfile and return its result and the profile's table."""
    profiler = cProfile.Profile()
    profiler.enable()
    result = function(*args)
    profiler.disable()
    return result, pstats.Stats(profiler)


def calls(stats, name):
    """How many times the function of that name ran: the table's rows are (file, line, name) -> (primitive calls, calls, own time, cumulative time, callers)."""
    return sum(row[1] for (file, line, func), row in stats.stats.items() if func == name)


def own_time(stats, name):
    return sum(row[2] for (file, line, func), row in stats.stats.items() if func == name)


APPEND = "<method 'append' of 'list' objects>"
points, queries = make_points(300), make_points(100)
answer, stats = profile(nearest, points, queries)
print(f"distance_squared: {calls(stats, 'distance_squared'):,} calls | nearest: {calls(stats, 'nearest')} call | list.append: {calls(stats, APPEND):,} calls")
print(f"distance_squared's own time is {own_time(stats, 'distance_squared') / stats.total_tt:.0%} of the profiled total")

_, doubled = profile(nearest, make_points(600), make_points(200))
print(f"doubling both inputs: {calls(doubled, 'distance_squared'):,} calls, {calls(doubled, 'distance_squared') / calls(stats, 'distance_squared'):.1f} times as many: the loop is quadratic")


def nearest_vectorized(points, queries):
    P, Q = np.array(points), np.array(queries)
    squared = ((Q[:, None, :] - P[None, :, :]) ** 2).sum(axis=2)
    return np.argmin(squared, axis=1).tolist()


fast, fast_stats = profile(nearest_vectorized, points, queries)
print(f"vectorized: {calls(fast_stats, 'distance_squared')} calls to distance_squared, same answers: {fast == answer}")

tracemalloc.start()
floats = [float(i) for i in range(100_000)]
_, list_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
array = np.arange(100_000, dtype=np.float64)
print(f"a list of 100,000 floats: {list_peak:,} bytes at peak | the array: {array.nbytes:,} bytes | the list took {list_peak / array.nbytes:.1f} times as much")
