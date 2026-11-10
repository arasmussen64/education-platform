import random

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


class Tracked:
    """A value that counts how often it is compared, whichever comparison is used."""

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


def test_the_output():
    """Prints the three lines."""
    assert run() == 'True False\n[9, 8, 8]\nversicolor setosa\n'


def test_a_sorted_chain_of_three_thousand():
    """3,000 values inserted in sorted order are all found, and a missing one is not."""
    bst_insert = function("bst_insert")
    bst_contains = function("bst_contains")
    root = None
    for value in range(3000):
        root = bst_insert(root, value)
    assert bst_contains(root, 2999) and bst_contains(root, 0) and not bst_contains(root, 3000)


def test_a_shuffled_tree_searches_quickly():
    """In a tree of 3,000 shuffled values, finding one takes fewer than 100 comparisons."""
    bst_insert = function("bst_insert")
    bst_contains = function("bst_contains")
    values = list(range(3000))
    random.Random(6).shuffle(values)
    root = None
    for value in tracked(values):
        root = bst_insert(root, value)
    Tracked.compared = 0
    assert bst_contains(root, Tracked(2999)) and not bst_contains(root, Tracked(-1))
    assert Tracked.compared < 100


def test_top_k_keeps_a_small_heap():
    """The 5 largest of 20,000 values are right, found with fewer than 170,180 comparisons."""
    top_k = function("top_k")
    rng = random.Random(5)
    stream = [rng.randint(1, 10**9) for _ in range(20_000)]
    Tracked.compared = 0
    result = top_k(tracked(stream), 5)
    assert [item.value for item in result] == sorted(stream, reverse=True)[:5]
    assert Tracked.compared < 170180


def test_decide():
    """A three-level tree classifies four records."""
    decide = function("decide")
    tree = ("age", 30, ("income", 50, "A", "B"), ("income", 20, "C", "D"))
    records = [{"age": 40, "income": 60}, {"age": 40, "income": 10}, {"age": 20, "income": 25}, {"age": 20, "income": 5}]
    assert [decide(tree, record) for record in records] == ["A", "B", "C", "D"]
