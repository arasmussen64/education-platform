from checks import function, run


def test_the_output():
    """Prints 4 1."""
    assert run() == '4 1\n'


def test_a_chain_and_a_star():
    """A chain has one leaf; a root with 50 children has 50."""
    leaves = function("leaves")
    chain = {"value": 0, "children": []}
    for i in range(1, 30):
        chain = {"value": i, "children": [chain]}
    assert leaves(chain) == 1
    assert leaves({"value": "r", "children": [{"value": i, "children": []} for i in range(50)]}) == 50
