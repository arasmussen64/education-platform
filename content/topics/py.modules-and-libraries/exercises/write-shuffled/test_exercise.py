import random

from checks import function


def test_same_items():
    """shuffled gives back the same items, as a list, possibly in another order."""
    shuffled = function("shuffled")
    result = shuffled([1, 2, 3, 4, 5])
    assert isinstance(result, list), f"shuffled returned {result!r}, not a list"
    assert sorted(result) == [1, 2, 3, 4, 5], f"shuffled returned {result!r}"


def test_original_untouched():
    """The list given is unchanged, and the result is a different list."""
    shuffled = function("shuffled")
    items = [1, 2, 3, 4, 5]
    result = shuffled(items)
    assert items == [1, 2, 3, 4, 5], f"the original became {items!r}"
    assert result is not items, "shuffled should return a new list"


def test_really_shuffles():
    """Over many tries, the order changes at least once."""
    shuffled = function("shuffled")
    random.seed(7)
    orders = set()
    for _ in range(20):
        orders.add(tuple(shuffled([1, 2, 3, 4, 5, 6])))
    assert len(orders) > 1, "shuffled never changed the order"
