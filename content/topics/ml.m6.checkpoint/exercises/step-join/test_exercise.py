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
    """Prints the three joined rows."""
    printed = run()
    assert printed == "[(1, 'Oslo'), (3, 'Lima'), (4, 'Oslo')]\n", f"Your program printed:\n{printed}"


def test_scales():
    """1,000 left records joined with 2,000 right records give 2,000 rows within 60,000 comparisons."""
    join = function("join")
    keys = tracked(range(1000))
    left = [{"k": key, "left": i} for i, key in enumerate(keys)]
    right = [{"k": keys[i % 1000], "right": i} for i in range(2000)]
    Tracked.compared = 0
    assert len(join(left, right, "k")) == 2000
    assert Tracked.compared < 60_000
