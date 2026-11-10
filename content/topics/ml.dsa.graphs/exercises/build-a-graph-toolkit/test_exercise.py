from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def grid(size):
    cells = {}
    for r in range(size):
        for c in range(size):
            cells[(r, c)] = [(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= r + dr < size and 0 <= c + dc < size]
    return cells


def test_the_output():
    """Prints the four lines."""
    assert run() == "{'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 2, 'F': 3}\n(20, ['A', 'C', 'E', 'D', 'F'])\n['load', 'clean', 'features', 'report', 'train', 'evaluate'] False\nTrue\n"


def test_hops_on_a_grid():
    """On a 40 by 40 grid, the opposite corner is 78 hops away and every cell is reached."""
    shortest_hops = function("shortest_hops")
    hops = shortest_hops(grid(40), (0, 0))
    assert len(hops) == 1600 and hops[(39, 39)] == 78 and hops[(0, 39)] == 39


def test_cheapest_takes_the_detour():
    """A direct road of 10 loses to a detour of 2 + 3 + 4, and an unreachable goal gives None."""
    cheapest_path = function("cheapest_path")
    roads = {"S": {"T": 10, "A": 2}, "A": {"B": 3}, "B": {"T": 4}, "T": {}, "X": {}}
    assert cheapest_path(roads, "S", "T") == (9, ["S", "A", "B", "T"])
    assert cheapest_path(roads, "S", "X") is None


def test_topological_order():
    """A chain of 400 steps comes out in chain order, a diamond respects its edges, and a cycle raises ValueError."""
    topological_order = function("topological_order")
    chain = {i: [i + 1] for i in range(399)}
    chain[399] = []
    assert topological_order(chain) == list(range(400))
    order = topological_order({"d": [], "a": ["b", "c"], "b": ["d"], "c": ["d"]})
    assert order.index("a") < order.index("b") < order.index("d") and order.index("a") < order.index("c") < order.index("d")
    try:
        topological_order({"a": ["b"], "b": ["c"], "c": ["a"]})
    except ValueError:
        pass
    else:
        raise AssertionError("a cycle should raise ValueError")


def test_has_cycle():
    """A self-loop and a two-node loop are cycles; a chain and a diamond are not."""
    has_cycle = function("has_cycle")
    assert has_cycle({"a": ["a"]}) and has_cycle({"x": [], "a": ["b"], "b": ["a"]})
    assert not has_cycle({"a": ["b"], "b": ["c"], "c": []}) and not has_cycle({"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []})
