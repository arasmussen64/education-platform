from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


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
    """Prints the counts, the distinct words, the group keys and the join."""
    assert run() == "{'the': 3, 'cat': 1, 'sat': 1, 'on': 1, 'mat': 1, 'end': 1}\n['the', 'cat', 'sat', 'on', 'mat', 'end']\n[1, 2, 9]\n[{'id': 1, 'name': 'Ada', 'item': 'book'}, {'id': 2, 'name': 'Grace', 'item': 'lamp'}, {'id': 2, 'name': 'Grace', 'item': 'pen'}]\n"


def test_count_frequencies_scales():
    """On 3,000 values with 100 distinct, the counts add up to 3,000 after fewer than 30,000 comparisons."""
    count_frequencies = function("count_frequencies")
    Tracked.compared = 0
    counts = count_frequencies(tracked([i % 100 for i in range(3000)]))
    assert len(counts) == 100 and sum(counts.values()) == 3000
    assert Tracked.compared < 30_000


def test_dedupe_scales():
    """On 3,000 values with 1,500 distinct, dedupe keeps the first-seen order after fewer than 30,000 comparisons."""
    dedupe = function("dedupe")
    Tracked.compared = 0
    result = dedupe(tracked([i % 1500 for i in range(3000)]))
    assert [item.value for item in result] == list(range(1500))
    assert Tracked.compared < 30_000


def test_join_scales():
    """Joining 1,000 left records with 2,000 right records on a key, each key matching twice, gives 2,000 rows after fewer than 60,000 comparisons."""
    join = function("join")
    left = [{"id": key} for key in tracked(range(1000))]
    right = [{"id": key, "n": i} for i, key in enumerate(tracked([i % 1000 for i in range(2000)]))]
    Tracked.compared = 0
    rows = join(left, right, "id")
    assert len(rows) == 2000 and rows[0]["id"].value == 0 and rows[0]["n"] == 0 and rows[1]["n"] == 1000
    assert Tracked.compared < 60_000


def test_group_by_keeps_every_record():
    """Grouping 6 records by a field with 2 values keeps all 6, 3 in each group."""
    group_by = function("group_by")
    groups = group_by([{"k": i % 2, "n": i} for i in range(6)], "k")
    assert sorted(groups) == [0, 1] and [r["n"] for r in groups[1]] == [1, 3, 5]
