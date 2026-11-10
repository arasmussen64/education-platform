from dataclasses import is_dataclass

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the one good order, then the positions 1, 2 and 3."""
    assert run() == "[Order(id=1, item='pen', qty=2)]\n[1, 2, 3]\n"


def test_good_records():
    """All-good records give Order dataclasses with the right fields and no bad positions."""
    load_orders = function("load_orders")
    orders, bad = load_orders('[{"id": 7, "item": "cup", "qty": 3}, {"id": 8, "item": "lid", "qty": 1}]')
    assert bad == []
    assert len(orders) == 2
    assert is_dataclass(orders[0])
    assert (orders[1].id, orders[1].item, orders[1].qty) == (8, "lid", 1)


def test_bad_records():
    """A float quantity, a record that's a number, a missing key and a string quantity are all bad."""
    load_orders = function("load_orders")
    text = '[{"id": 1, "item": "pen", "qty": 2.0}, 7, {"item": "x", "qty": 1}, {"id": 9, "item": "y", "qty": 3}, {"id": 5, "item": "z", "qty": "5"}]'
    orders, bad = load_orders(text)
    assert bad == [0, 1, 2, 4]
    assert [(o.id, o.item, o.qty) for o in orders] == [(9, "y", 3)]
    assert load_orders("[]") == ([], [])
