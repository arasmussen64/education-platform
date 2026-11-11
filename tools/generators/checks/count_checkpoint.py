"""Count comparisons for the checkpoint build (solution and wrong versions) with the tests' Tracked/Ordered wrappers."""
import contextlib
import io
import random
import runpy
import sys


class Tracked:
    compared = 0

    def __init__(self, value):
        self.value = value

    def _count(self):
        Tracked.compared += 1

    def __eq__(self, other):
        self._count()
        return self.value == other.value

    def __lt__(self, other):
        self._count()
        return self.value < other.value

    def __le__(self, other):
        self._count()
        return self.value <= other.value

    def __gt__(self, other):
        self._count()
        return self.value > other.value

    def __ge__(self, other):
        self._count()
        return self.value >= other.value

    def __hash__(self):
        return hash(self.value)


class Ordered:
    compared = 0

    def __init__(self, value):
        self.value = value

    def _count(self):
        Ordered.compared += 1

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        self._count()
        return self.value < other.value

    def __le__(self, other):
        self._count()
        return self.value <= other.value

    def __gt__(self, other):
        self._count()
        return self.value > other.value

    def __ge__(self, other):
        self._count()
        return self.value >= other.value

    def __hash__(self):
        return hash(self.value)


def tracked(values):
    return [Tracked(v) for v in values]


def ordered(values):
    return [Ordered(v) for v in values]


def load(path):
    with contextlib.redirect_stdout(io.StringIO()):
        return runpy.run_path(path)


for path in sys.argv[1:]:
    ns = load(path)
    print("=====", path)
    if "dedupe" in ns:
        dedupe = ns["dedupe"]
        records = [{"key": key, "n": i} for i, key in enumerate(tracked(i % 1500 for i in range(3000)))]
        Tracked.compared = 0
        kept = dedupe(records, "key")
        print("dedupe comparisons:", Tracked.compared, "right:", [r["n"] for r in kept] == list(range(1500)), "(budget < 30,000)")
    if "top_k" in ns:
        top_k = ns["top_k"]
        rng = random.Random(7)
        values = [rng.randint(1, 10**9) for _ in range(20_000)]
        records = [{"v": value} for value in ordered(values)]
        Ordered.compared = 0
        result = top_k(records, "v", 5)
        right = [r["v"].value for r in result] == sorted(values, reverse=True)[:5]
        print("top_k Ordered comparisons:", Ordered.compared, "right:", right, "(budget < 170,151)")
        Ordered.compared = 0
        sorted(records, key=lambda r: r["v"], reverse=True)[:5]
        print("  sorted(..., key, reverse=True) Ordered comparisons:", Ordered.compared)
        Ordered.compared = 0
        sorted(records, key=lambda r: r["v"])[-5:]
        print("  sorted(..., key) Ordered comparisons:", Ordered.compared)
    if "join" in ns:
        join = ns["join"]
        keys = tracked(range(1000))
        left = [{"k": key, "left": i} for i, key in enumerate(keys)]
        right = [{"k": keys[i % 1000], "right": i} for i in range(2000)]
        Tracked.compared = 0
        rows = join(left, right, "k")
        ok = len(rows) == 2000 and rows[0]["left"] == 0 and rows[0]["right"] == 0 and rows[1]["right"] == 1000
        print("join comparisons:", Tracked.compared, "right:", ok, "(budget < 60,000)")
