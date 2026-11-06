from checks import run


def test_heading_then_blank_line():
    """Starts with the heading, then a blank line."""
    lines = run().splitlines()
    assert lines[:1] == ["Shopping list"], "The first line should be: Shopping list"
    assert lines[1:2] == [""], "The second line should be empty."


def test_items_in_order():
    """Then lists apples, bread and milk, one per line, and nothing else."""
    printed = run()
    assert printed.splitlines()[2:] == ["apples", "bread", "milk"], (
        "After the blank line should come apples, bread and milk, each on its "
        f"own line. Your program printed:\n{printed}"
    )
