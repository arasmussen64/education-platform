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


def values(items):
    return [item.value for item in items]


def test_the_output():
    """Prints the three lines."""
    assert run() == "[1, 2, 5, 5, 6, 9] [1, 2, 5, 5, 6, 9]\n3 -1\n['bob', 'dee', 'ann']\n"


def test_insertion_sort_on_sorted_input():
    """3,000 items already in order are sorted with fewer than 6,000 comparisons, and a shuffled list comes out sorted."""
    insertion_sort = function("insertion_sort")
    Tracked.compared = 0
    assert values(insertion_sort(tracked(range(3000)))) == list(range(3000))
    assert Tracked.compared < 6000
    data = list(range(200))
    random.Random(3).shuffle(data)
    assert values(insertion_sort(tracked(data))) == list(range(200))


def test_merge_sort_scales():
    """3,000 shuffled items are sorted with fewer than 60,000 comparisons."""
    merge_sort = function("merge_sort")
    data = list(range(3000))
    random.Random(4).shuffle(data)
    Tracked.compared = 0
    assert values(merge_sort(tracked(data))) == list(range(3000))
    assert Tracked.compared < 60_000


def test_binary_search_halves():
    """The last of 100,000 items is found, and a missing one reported, within 80 comparisons."""
    binary_search = function("binary_search")
    items = tracked(range(0, 200_000, 2))
    Tracked.compared = 0
    assert binary_search(items, Tracked(199_998)) == 99_999 and binary_search(items, Tracked(199_999)) == -1
    assert Tracked.compared <= 80


def test_top_k_by():
    """Ties keep their original order, and k larger than the list returns everything."""
    top_k_by = function("top_k_by")
    records = [{"n": "a", "v": 1}, {"n": "b", "v": 3}, {"n": "c", "v": 3}, {"n": "d", "v": 2}]
    assert [r["n"] for r in top_k_by(records, "v", 2)] == ["b", "c"]
    assert [r["n"] for r in top_k_by(records, "v", 10)] == ["b", "c", "d", "a"]
