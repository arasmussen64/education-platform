from checks import function, run

EXPECTED = "[{'id': 1, 'name': 'Ada', 'item': 'book'}, {'id': 2, 'name': 'Grace', 'item': 'lamp'}, {'id': 2, 'name': 'Grace', 'item': 'pen'}]\n2000\n"


class Tracked:
    """A value that counts how often it is compared. Hashing is free; == is counted."""

    compared = 0

    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        Tracked.compared += 1
        return self.value == other.value

    def __lt__(self, other):
        Tracked.compared += 1
        return self.value < other.value


def tracked(values):
    return [Tracked(v) for v in values]


def test_the_output():
    """Prints the small join and 2000."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_group_by_keeps_every_record():
    """Grouping 6 records by a field with 2 values keeps all 6."""
    group_by = function("group_by")
    groups = group_by([{"k": i % 2, "n": i} for i in range(6)], "k")
    assert [r["n"] for r in groups[0]] == [0, 2, 4] and [r["n"] for r in groups[1]] == [1, 3, 5]


def test_join_scales():
    """Joining 1,000 left records with 2,000 right records gives 2,000 rows after fewer than 60,000 comparisons."""
    join = function("join")
    left = [{"id": key} for key in tracked(range(1000))]
    right = [{"id": key, "n": i} for i, key in enumerate(tracked([i % 1000 for i in range(2000)]))]
    Tracked.compared = 0
    rows = join(left, right, "id")
    assert len(rows) == 2000
    assert Tracked.compared < 60_000, f"{Tracked.compared} comparisons, where fewer than 60,000 are expected"
