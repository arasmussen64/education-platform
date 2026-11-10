from checks import function, run


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
    """Prints the five results."""
    assert run() == '0 9 5\n-1 -1\n'


def test_halves():
    """100,000 items are searched within 80 comparisons."""
    binary_search = function("binary_search")
    items = tracked(range(0, 200_000, 2))
    Tracked.compared = 0
    assert binary_search(items, Tracked(199_998)) == 99_999 and binary_search(items, Tracked(3)) == -1
    assert Tracked.compared <= 80
