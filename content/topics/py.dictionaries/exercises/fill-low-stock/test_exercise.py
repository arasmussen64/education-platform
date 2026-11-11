from checks import run, run_with


def test_this_stock():
    """Prints each fruit with its count, then ['apples', 'plums']."""
    got = run()
    assert got == "apples: 3\npears: 12\nplums: 0\n['apples', 'plums']\n", f"Your program printed:\n{got}"


def test_other_stock():
    """For 9 kiwis, 1 lime and 4 melons it lists them, then prints ['limes', 'melons']."""
    got = run_with({"stock": {"kiwis": 9, "limes": 1, "melons": 4}})
    assert got == "kiwis: 9\nlimes: 1\nmelons: 4\n['limes', 'melons']\n", (
        f"With 9 kiwis, 1 lime and 4 melons in stock, your program printed:\n{got}"
    )
