import cProfile
import pstats


def heavy():
    total = 0
    for i in range(1_000_000):
        total += i * i
    return total


def light():
    total = 0
    for i in range(100):
        total += i
    return total


def run():
    for _ in range(500):
        light()
    return heavy()


profiler = cProfile.Profile()
profiler.enable()
run()
profiler.disable()
print(hot_spots(pstats.Stats(profiler), 2))
