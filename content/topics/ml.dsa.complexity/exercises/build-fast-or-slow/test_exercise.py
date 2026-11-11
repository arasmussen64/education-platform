from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


class Tracked:
    """A value that counts how often it is compared. Hashing is free; == and < are counted."""

    compared = 0

    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        Tracked.compared += 1
        # A solution may compare an item with something that isn't an item,
        # such as `previous = None` before a loop over sorted items. That is
        # simply "not equal"; without this line it crashed the hidden test.
        if not isinstance(other, Tracked):
            return NotImplemented
        return self.value == other.value

    def __lt__(self, other):
        Tracked.compared += 1
        return self.value < other.value


def tracked(values):
    return [Tracked(v) for v in values]


def test_the_output():
    """Prints the four lines."""
    assert run() == '45 499500\nTrue False\n2 2500\nquadratic linear\n'


def test_pairs():
    """pairs(1) is 0, pairs(2) is 1, pairs(3000) is 4,498,500."""
    pairs = function("pairs")
    assert (pairs(1), pairs(2), pairs(3000)) == (0, 1, 4498500)


def test_has_duplicate_scales():
    """On 3,000 distinct items, has_duplicate compares elements fewer than 60,000 times (a nested loop makes 4,498,500), and still finds a repeat."""
    has_duplicate = function("has_duplicate")
    Tracked.compared = 0
    assert not has_duplicate(tracked(range(3000)))
    assert Tracked.compared < 60_000
    assert has_duplicate(tracked([5, 2, 5]))


def test_common_count_scales():
    """On two lists of 3,000 with 1,000 values in common, common_count is 1,000 after fewer than 120,000 comparisons."""
    common_count = function("common_count")
    Tracked.compared = 0
    assert common_count(tracked(range(3000)), tracked(range(2000, 5000))) == 1000
    assert Tracked.compared < 120_000
    assert common_count(tracked([1, 1, 2]), tracked([1, 1, 1])) == 1


def test_growth_name():
    """A flat count is constant, an n log n count reads as linear, cubic growth is faster than quadratic."""
    growth_name = function("growth_name")
    assert growth_name([1000, 1000, 1001]) == "constant"
    assert growth_name([10000, 22000, 48000]) == "linear"
    assert growth_name([1, 8, 64]) == "faster than quadratic"
