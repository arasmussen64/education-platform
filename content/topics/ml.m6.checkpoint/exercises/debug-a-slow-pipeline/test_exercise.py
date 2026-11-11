from checks import function, run

EXPECTED = "7 events, 5 distinct\n[9, 12, 7]\n[(7, 'Oslo'), (3, 'Lima'), (9, 'Pune'), (15, 'Oslo')]\n('Pune', 2)\n['load', 'clean', 'join', 'features', 'train', 'report']\n"


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
    """Prints the five lines: the counts, the top three, the join, the closest name and the schedule."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_dedupe_scales():
    """3,000 records with 1,500 distinct keys dedupe within 30,000 comparisons."""
    dedupe = function("dedupe")
    records = [{"key": key, "n": i} for i, key in enumerate(tracked(i % 1500 for i in range(3000)))]
    Tracked.compared = 0
    assert len(dedupe(records, "key")) == 1500
    assert Tracked.compared < 30_000, f"{Tracked.compared} comparisons, where fewer than 30,000 are expected"


def test_schedule_is_a_queue():
    """Steps that became ready first run first: b before c when both wait only on a."""
    schedule = function("schedule")
    assert schedule({"a": [], "b": ["a"], "c": ["a"], "d": ["c", "b"]}) == ["a", "b", "c", "d"]


def test_edit_distance():
    """kitten to sitting is 3, flaw to lawn is 2, and a string to itself is 0."""
    edit_distance = function("edit_distance")
    assert (edit_distance("kitten", "sitting"), edit_distance("flaw", "lawn"), edit_distance("same", "same")) == (3, 2, 0)
