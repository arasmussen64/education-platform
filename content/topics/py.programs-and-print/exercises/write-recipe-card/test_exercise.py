from checks import run

INGREDIENTS = ["2 eggs", "1 cup of flour", "1 cup of milk"]


def test_title_then_blank_line():
    """Starts with the title, Pancakes, then a blank line."""
    lines = run().splitlines()
    assert lines[:1] == ["Pancakes"], "The first line should be: Pancakes"
    assert lines[1:2] == [""], "The second line should be empty."


def test_ingredients_in_order():
    """Then lists the three ingredients, one per line, and nothing else."""
    printed = run()
    assert printed.splitlines()[2:] == INGREDIENTS, (
        "After the blank line should come the three ingredients, exactly as "
        f"shown, one per line. Your program printed:\n{printed}"
    )
