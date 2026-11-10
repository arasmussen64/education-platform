from checks import function, run


def test_the_output():
    """Prints False, True, False."""
    printed = run()
    assert printed == 'False\nTrue\nFalse\n', f"Your program printed:\n{printed}"


def test_more_graphs():
    """A self-loop is a cycle; a chain of 300 nodes is not; a cycle away from the first node is still found."""
    has_cycle = function("has_cycle")
    assert has_cycle({"a": ["a"]})
    chain = {i: [i + 1] for i in range(299)}
    chain[299] = []
    assert not has_cycle(chain)
    assert has_cycle({"a": [], "b": ["c"], "c": ["b"]})
