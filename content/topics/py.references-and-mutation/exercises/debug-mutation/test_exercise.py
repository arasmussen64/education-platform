from checks import function, run


def test_program():
    """Prints ['milk', 'tea'], then ['milk', 'eggs'], then ['milk']."""
    got = run()
    assert got == "['milk', 'tea']\n['milk', 'eggs']\n['milk']\n", f"Your program printed:\n{got}"


def test_add_item_keeps_original():
    """add_item returns a new list and leaves the one it was given unchanged."""
    add_item = function("add_item")
    items = ["a"]
    result = add_item(items, "b")
    assert result == ["a", "b"], f"add_item returned {result!r}"
    assert items == ["a"], f"the list given to add_item became {items!r}"
