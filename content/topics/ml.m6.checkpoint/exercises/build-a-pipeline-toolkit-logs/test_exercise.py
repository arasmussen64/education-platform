import random

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


class Tracked:
    """A value that counts how often it is compared, whichever comparison is used; hashing is free."""

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


class Ordered:
    """A value that counts only its ordering comparisons: tuples in a heap test equality first, and that test is free here."""

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


def ordered(values):
    return [Ordered(v) for v in values]


def test_the_output():
    """Prints the five lines."""
    assert run() == "8 lines, 6 requests\n['r2', 'r4', 'r5']\n[('r1', 'discovery'), ('r2', 'money'), ('r3', 'identity'), ('r4', 'money'), ('r5', 'discovery')]\n('payment', 2)\n['build', 'test', 'scan', 'stage', 'smoke', 'release']\n"


def test_dedupe_scales():
    """3,000 records with 1,500 distinct keys dedupe to 1,500, first-seen first, within 30,000 comparisons (a list for seen makes 2,250,000)."""
    dedupe = function("dedupe")
    records = [{"key": key, "n": i} for i, key in enumerate(tracked(i % 1500 for i in range(3000)))]
    Tracked.compared = 0
    kept = dedupe(records, "key")
    assert [record["n"] for record in kept] == list(range(1500))
    assert Tracked.compared < 30_000


def test_top_k_scales():
    """The 5 largest of 20,000 records are right, found within 170,151 comparisons (sorting everything makes about 260,314)."""
    top_k = function("top_k")
    rng = random.Random(7)
    values = [rng.randint(1, 10**9) for _ in range(20_000)]
    records = [{"v": value} for value in ordered(values)]
    Ordered.compared = 0
    result = top_k(records, "v", 5)
    assert [record["v"].value for record in result] == sorted(values, reverse=True)[:5]
    assert Ordered.compared < 170151


def test_join_scales():
    """1,000 left records joined with 2,000 right records, each key matching twice, give 2,000 rows in left order within 60,000 comparisons (a scan makes 2 million)."""
    join = function("join")
    keys = tracked(range(1000))
    left = [{"k": key, "left": i} for i, key in enumerate(keys)]
    right = [{"k": keys[i % 1000], "right": i} for i in range(2000)]
    Tracked.compared = 0
    rows = join(left, right, "k")
    assert len(rows) == 2000 and rows[0]["left"] == 0 and rows[0]["right"] == 0 and rows[1]["right"] == 1000
    assert Tracked.compared < 60_000


def test_closest_name():
    """kitten is closest to mitten (1 edit), a tie keeps the first name, and an exact match is distance 0."""
    closest_name = function("closest_name")
    assert closest_name("kitten", ["sitting", "mitten", "bitten"]) == ("mitten", 1)
    assert closest_name("ab", ["ac", "cb"]) == ("ac", 1)
    assert closest_name("same", ["other", "same"]) == ("same", 0)


def test_schedule():
    """A chain of 300 steps runs in chain order, a diamond respects its dependencies, and a cycle raises ValueError."""
    schedule = function("schedule")
    chain = {"s0": []}
    for i in range(1, 300):
        chain[f"s{i}"] = [f"s{i - 1}"]
    assert schedule(chain) == [f"s{i}" for i in range(300)]
    order = schedule({"d": ["b", "c"], "a": [], "b": ["a"], "c": ["a"]})
    assert order.index("a") < order.index("b") < order.index("d") and order.index("a") < order.index("c") < order.index("d")
    try:
        schedule({"a": ["b"], "b": ["c"], "c": ["a"]})
    except ValueError:
        pass
    else:
        raise AssertionError("a cycle should raise ValueError")
