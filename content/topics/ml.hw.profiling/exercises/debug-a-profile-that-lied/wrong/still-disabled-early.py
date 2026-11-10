import cProfile
import pstats


def heavy():
    total = 0
    for i in range(200_000):
        total += i * i
    return total


def light():
    return 1


def run():
    for _ in range(1_000):
        light()
    return heavy()


profiler = cProfile.Profile()
profiler.enable()
profiler.disable()
run()
stats = pstats.Stats(profiler)
rows = [(func, row[1], row[2]) for (file, line, func), row in stats.stats.items() if file != "~"]
rows.sort(key=lambda row: row[2], reverse=True)
print("most own time:", rows[0][0], "| calls to light:", next(count for func, count, own in rows if func == "light"))
