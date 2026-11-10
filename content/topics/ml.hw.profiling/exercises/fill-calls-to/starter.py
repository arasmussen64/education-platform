import cProfile
import pstats


def step(i):
    return i * 2


def work(n):
    return [step(i) for i in range(n)]


def calls_to(stats, name):
    """How many times the function called name ran, read from the profile's table; 0 if it never did."""
    for (file, line, func), (primitive, total, own, cumulative, callers) in stats.stats.items():
        if func == ...:
            return ...
    return 0


profiler = cProfile.Profile()
profiler.enable()
work(250)
profiler.disable()
stats = pstats.Stats(profiler)
print(calls_to(stats, "step"), calls_to(stats, "work"), calls_to(stats, "never"))
