import cProfile
import pstats


def heavy():
    total = 0
    for i in range(100_000):
        total += i * i
    return total


def light():
    total = 0
    for i in range(10):
        total += i
    return total


def run():
    for _ in range(500):
        light()
    return heavy()


def hot_spots(stats, k):
    """The names of the k functions with the most own time, largest first, leaving out the built-ins (their file is '~')."""
    rows = [(row[2], func) for (file, line, func), row in stats.stats.items() if file != "~"]
    rows.sort(reverse=True)
    return [func for own, func in rows[:k]]


profiler = cProfile.Profile()
profiler.enable()
run()
profiler.disable()
print(hot_spots(pstats.Stats(profiler), 2))
