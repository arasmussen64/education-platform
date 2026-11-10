from checks import function, run


def test_the_output():
    """Prints 8 4 and 1 1."""
    printed = run()
    assert printed == '8 4\n1 1\n', f"Your program printed:\n{printed}"


def test_a_chain_and_a_star():
    """A chain of 200 nodes has size 200 and depth 200; a root with 1,000 leaves has size 1,001 and depth 2."""
    size = function("size")
    depth = function("depth")
    chain = {"value": 0, "children": []}
    for i in range(1, 200):
        chain = {"value": i, "children": [chain]}
    assert (size(chain), depth(chain)) == (200, 200)
    star = {"value": "root", "children": [{"value": i, "children": []} for i in range(1000)]}
    assert (size(star), depth(star)) == (1001, 2)
