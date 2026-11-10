import time


def has_duplicate_slow(items, counter):
    """Compare every pair of items: a loop inside a loop."""
    n = len(items)
    for i in range(n):
        for j in range(i + 1, n):
            counter[0] += 1
            if items[i] == items[j]:
                return True
    return False


def has_duplicate_fast(items, counter):
    """One pass, remembering what has been seen in a set."""
    seen = set()
    for item in items:
        counter[0] += 1
        if item in seen:
            return True
        seen.add(item)
    return False


def steps(function, items):
    counter = [0]
    function(items, counter)
    return counter[0]


def seconds(function, items, repeats):
    """The best of two timings, each of `repeats` runs, per run: many runs of a fast function give the clock something to measure."""
    best = float("inf")
    for _ in range(2):
        start = time.perf_counter()
        for _ in range(repeats):
            function(items, [0])
        best = min(best, (time.perf_counter() - start) / repeats)
    return best


for n in (500, 1000, 2000):
    items = list(range(n))
    print(n, "slow", steps(has_duplicate_slow, items), "fast", steps(has_duplicate_fast, items))

slow_ratio = steps(has_duplicate_slow, list(range(2000))) / steps(has_duplicate_slow, list(range(1000)))
print("steps from 1000 to 2000: slow x", round(slow_ratio, 2), "fast x", round(2000 / 1000, 2))

slow_800 = seconds(has_duplicate_slow, list(range(800)), 1)
slow_1600 = seconds(has_duplicate_slow, list(range(1600)), 1)
fast_1600 = seconds(has_duplicate_fast, list(range(1600)), 50)
print("time from 800 to 1600: slow x", round(slow_1600 / max(slow_800, 1e-9), 1))
print("at 1600, slow takes", round(slow_1600 / max(fast_1600, 1e-9)), "times longer than fast")
