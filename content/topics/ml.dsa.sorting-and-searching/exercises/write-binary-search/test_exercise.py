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
    printed = run()
    assert printed == '0 9 5\n-1 -1\n', f"Your program printed:\n{printed}"


def test_a_hundred_thousand_items():
    """The last of 100,000 items is found, and a missing one reported, within 80 comparisons in all."""
    binary_search = function("binary_search")
    items = tracked(range(0, 200_000, 2))
    Tracked.compared = 0
    assert binary_search(items, Tracked(199_998)) == 99_999
    assert binary_search(items, Tracked(199_999)) == -1
    assert Tracked.compared <= 80, f"{Tracked.compared} comparisons: halve, don't scan"
