"""Count comparisons for the trees-and-heaps build exercise, solution and wrong versions."""
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


def tracked(values):
    return [Tracked(v) for v in values]


def load(path):
    with contextlib.redirect_stdout(io.StringIO()):
        return runpy.run_path(path)


for path in sys.argv[1:]:
    ns = load(path)
    print("=====", path)
    bst_insert = ns["bst_insert"]
    bst_contains = ns["bst_contains"]
    top_k = ns["top_k"]
    # shuffled tree search
    values = list(range(3000))
    random.Random(6).shuffle(values)
    root = None
    for value in tracked(values):
        root = bst_insert(root, value)
    Tracked.compared = 0
    ok = bst_contains(root, Tracked(2999)) and not bst_contains(root, Tracked(-1))
    print("shuffled search comparisons:", Tracked.compared, "ok:", ok, "(budget < 100)")
    # top_k on 20,000
    rng = random.Random(5)
    stream = [rng.randint(1, 10**9) for _ in range(20_000)]
    Tracked.compared = 0
    result = top_k(tracked(stream), 5)
    right = [item.value for item in result] == sorted(stream, reverse=True)[:5]
    print("top_k comparisons:", Tracked.compared, "right:", right, "(budget < 170180)")
    # sorting everything
    Tracked.compared = 0
    sorted(tracked(stream), reverse=True)[:5]
    print("sorted(reverse=True) comparisons:", Tracked.compared)
    Tracked.compared = 0
    sorted(tracked(stream))[-5:]
    print("sorted() comparisons:", Tracked.compared)
    # sorted chain of 3000
    try:
        root = None
        for value in range(3000):
            root = bst_insert(root, value)
        print("chain ok:", bst_contains(root, 2999) and bst_contains(root, 0) and not bst_contains(root, 3000))
    except RecursionError as e:
        print("chain RecursionError:", e)
