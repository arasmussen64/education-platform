from checks import function, run

EXPECTED = "1500 ['user0@example.com', 'user1@example.com'] user1499@example.com\n"


class Tracked:
    """A value that counts how often it is compared. Hashing is free; == and < are counted."""

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
    """Prints 1500 distinct emails, first appearance first."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\n{EXPECTED}\nYour program printed:\n{printed}"


def test_scales():
    """On 3,000 values with 1,500 distinct, the function compares fewer than 30,000 times (a list makes about 2 million) and keeps the first-seen order."""
    unique_in_order = function("unique_in_order")
    values = tracked([i % 1500 for i in range(3000)])
    Tracked.compared = 0
    result = unique_in_order(values)
    assert [item.value for item in result] == list(range(1500)), "the order or the set of values is wrong"
    assert Tracked.compared < 30_000, f"{Tracked.compared} comparisons: seen must be a set"
