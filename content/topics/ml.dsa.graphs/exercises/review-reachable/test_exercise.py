from checks import function, run


def test_the_output():
    """Prints the three sorted sets."""
    assert run() == "['a', 'b', 'c'] ['a', 'b', 'c', 'd'] ['c']\n"


def test_a_cycle_terminates():
    """A graph that is one big cycle is fully reachable from any node, and the search ends."""
    reachable = function("reachable")
    ring = {i: [(i + 1) % 500] for i in range(500)}
    assert reachable(ring, 0) == set(range(500))
