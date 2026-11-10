from checks import function, run


def test_the_output():
    """Prints the order and the cycle's message."""
    printed = run()
    assert printed == "['load', 'clean', 'join', 'features', 'train']\nthe steps depend on each other in a cycle\n", f"Your program printed:\n{printed}"


def test_a_diamond_and_a_chain():
    """A diamond runs its two middle steps in the order they became ready, and a chain of 50 runs in chain order."""
    schedule = function("schedule")
    assert schedule({"d": ["c", "b"], "a": [], "b": ["a"], "c": ["a"]}) == ["a", "b", "c", "d"]
    chain = {"s0": []}
    for i in range(1, 50):
        chain[f"s{i}"] = [f"s{i - 1}"]
    assert schedule(chain) == [f"s{i}" for i in range(50)]
