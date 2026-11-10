from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the inventory, then its total."""
    assert run() == "Inventory({'pen': 12, 'ink': 2})\n14\n"


def test_counts_and_total():
    """add starts a new item at 0, remove subtracts, total adds everything up."""
    Inventory = function("Inventory")
    shelf = Inventory()
    shelf.add("cup", 4)
    shelf.add("cup", 1)
    shelf.remove("cup", 2)
    shelf.add("plate", 6)
    assert shelf.counts == {"cup": 3, "plate": 6}
    assert shelf.total() == 9


def test_instances_are_separate():
    """Two inventories keep their own counts."""
    Inventory = function("Inventory")
    first = Inventory()
    second = Inventory()
    first.add("pen", 1)
    assert second.counts == {}
    assert second.total() == 0
    assert repr(second) == "Inventory({})"
