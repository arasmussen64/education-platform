from checks import run, run_with


def test_three_items():
    """Prints the first and last items, the changed list, its length, and a line per item."""
    assert run() == (
        "milk\neggs\n['milk', 'rolls', 'eggs', 'tea']\n4\n"
        "buy milk\nbuy rolls\nbuy eggs\nbuy tea\n"
    )


def test_two_items():
    """Works for a list of two items as well."""
    assert run_with({"shopping": ["a", "b"]}) == (
        "a\nb\n['a', 'rolls', 'tea']\n3\nbuy a\nbuy rolls\nbuy tea\n"
    )
