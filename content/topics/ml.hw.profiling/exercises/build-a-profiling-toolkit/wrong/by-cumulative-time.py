import cProfile
import pstats
import tracemalloc


def profile(function, *args):
    """Run the function under cProfile; return its result and the profile's table."""
    profiler = cProfile.Profile()
    profiler.enable()
    result = function(*args)
    profiler.disable()
    return result, pstats.Stats(profiler)


def call_counts(stats):
    """name -> how many times it ran, for the Python-level functions only (cProfile files the built-ins under '~')."""
    return {func: row[1] for (file, line, func), row in stats.stats.items() if file != "~"}


def hot_spots(stats, k):
    """The k Python-level functions with the most own time, largest first."""
    rows = [(row[3], func) for (file, line, func), row in stats.stats.items() if file != "~"]
    rows.sort(reverse=True)
    return [func for own, func in rows[:k]]


def peak_bytes(function, *args):
    """The most memory the function had allocated at any moment while it ran, in bytes."""
    tracemalloc.start()
    function(*args)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def growth(function, make_input, n, name):
    """How many times more often name is called when the input size doubles from n to 2n."""
    _, small = profile(function, make_input(n))
    _, large = profile(function, make_input(2 * n))
    return call_counts(large)[name] / call_counts(small)[name]


def leaf(x):
    return x + 1


def branch(n):
    total = 0
    for i in range(n):
        total += leaf(i)
    return total


def root(n):
    return branch(n) + branch(n)


def pairs(items):
    total = 0
    for a in items:
        for b in items:
            total += leaf(a)
    return total


def tap():
    return 1


def grind(n):
    total = 0
    for i in range(n):
        total += i * i
    return total


def run():
    for _ in range(50):
        tap()
    return grind(100_000)


result, stats = profile(root, 1000)
counts = call_counts(stats)
print(result, counts["leaf"], counts["branch"], counts["root"], sorted(counts))
_, grind_stats = profile(run)
print(hot_spots(grind_stats, 1))
print(peak_bytes(lambda: [float(i) for i in range(50_000)]) > 50_000 * 8)
print(growth(branch, lambda n: n, 500, "leaf"), growth(pairs, lambda n: list(range(n)), 50, "leaf"))
