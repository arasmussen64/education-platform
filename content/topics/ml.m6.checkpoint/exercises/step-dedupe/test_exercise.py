from checks import function, run


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
    """Prints the three distinct ids."""
    printed = run()
    assert printed == '[7, 3, 9]\n', f"Your program printed:\n{printed}"


def test_scales():
    """3,000 records with 1,500 distinct keys dedupe within 30,000 comparisons."""
    dedupe = function("dedupe")
    records = [{"key": key, "n": i} for i, key in enumerate(tracked(i % 1500 for i in range(3000)))]
    Tracked.compared = 0
    assert len(dedupe(records, "key")) == 1500
    assert Tracked.compared < 30_000
